from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, List, Dict
import pandas as pd

from line import Line


class Economics(BaseModel):
    """Economics‑tab – financial assumptions."""
    conductors_lifetime: int
    structures_lifetime: int
    wacc: float = Field(..., ge=0, le=1, description="Cost of capital (fraction)")
    inflation: float = Field(..., ge=0, le=1)
    cost_of_structures_unit: float = Field(..., ge=0, description="Cost per structure (dollars)")
    cost_of_losses_dol_per_mwh: float = Field(..., ge=0, description="Cost of losses per MWh (dollars)")
    cost_of_congestion_dol_per_mwh: float = Field(..., ge=0, description="Congestion cost per MW (dollars)")


class Project(Line, Economics):
    prj_name: Optional[str] = "New Line"
    time_horizon: int = Field(..., ge=1, description="Time horizon for NPV calculation (years)")
    replace_cd_at: int = Field(..., ge=0, description="Year at which conductor replacement is planned, corresponding to conductors_remaining_life.")
    replace_st_at: int = Field(..., ge=0, description="Year at which structure replacement is planned, corresponding to structures_remaining_life.")
    
    consider_losses: Optional[bool] = True
    consider_corona : Optional[bool] = False
    consider_str_type: Optional[bool] = False
    filter_type: Optional[bool] = False


    # ----- Helper methods for calculations (called by the main calculation methods) -----    
    
    def _get_conductors_for_cost_calc(self):
        
        conductors = pd.DataFrame([c.dict() for c in self.conductors_list])
        
        conductors = conductors.reset_index(drop=True)
        desired_cols = ['code', 'type', 'dol_per_1000_ft', 'inst_dol_per_1000_ft', 'str_costs_dol',
            'accessories_dol_per_1000_ft', 'env_ampacity_a', 'peak_current', 'temp_at_current_c', 'max_temperature_c',
            'sag_m', 'tension_n', 'losses_at_peak_mwh_per_m', 'inception_voltage_kv', 'structure_type', 'total_force',
            'congestion_mw', 'corona_losses_mwh_per_m']
        valid_cols = conductors.columns.intersection(desired_cols)
        conductors = conductors[valid_cols].copy()
        
        return conductors


    def _structure_costs(self, time_horizon=100, replace_st_at=0, st={}):

        str_data = st
        if str_data and 'line_angle' in str_data:
            self.cost_of_structures_unit = (str_data['str_tgt'] * str_data['str_tgt_cost']
                                        + str_data['str_ra'] * str_data['str_ra_cost']
                                        + str_data['str_nade'] * str_data['str_nade_cost']
                                        + str_data['str_ade'] * str_data['str_ade_cost']) / str_data['nbr_structures']
            self.nbr_structures = str_data['nbr_structures']

        c = self._get_conductors_for_cost_calc()

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

        npv[['structures_inv', 'conductors_inv']] = 0
        npv.loc[npv.year.isin(range(replace_st_at, time_horizon, self.structures_lifetime)), 'structures_inv'] = 1
        npv['cost_capital'] = npv.year.apply(lambda x: 1 / (1 + self.wacc)**x)

        # if not self.customize_inv_options:
        structures = c.str_costs_dol.apply(lambda r: npv['inflation'] * self.cost_of_structures_unit * npv['structures_inv'] * self.nbr_structures)
        # else:
        #     structures = c.str_costs_dol.apply(lambda r: r * npv['inflation'] * npv['structures_inv'])
        
        c['prj_name'] = self.prj_name

        cost_st = structures * npv['cost_capital'] / 1e6
        cost_st = c[['code', 'type', 'prj_name']].join(cost_st.cumsum(axis=1))
        
        return cost_st
    
    
    def _conductor_costs(self, time_horizon=100, replace_cd_at=0, structures={}, nbr_phases=3):

        c = self._get_conductors_for_cost_calc()

        nbr_conds = 1 if 'nbr_conductors' not in structures else structures['nbr_conductors']

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

        npv['conductors_inv'] = 0
        npv.loc[npv.year.isin(range(replace_cd_at, time_horizon, self.conductors_lifetime)), 'conductors_inv'] = 1
        npv['cost_capital'] = npv['year'].apply(lambda x: 1 / (1 + self.wacc)**x)

        length_kft = self.length_km * 3.28
        conductor_inv = c.dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                                                    * length_kft * self.nbr_ckts * nbr_phases * nbr_conds
        conductor_inst = c.inst_dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                                                    * length_kft * self.nbr_ckts * nbr_phases * nbr_conds
        conductor_access = c.accessories_dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                        * length_kft * self.nbr_ckts * nbr_phases * nbr_conds

        prj = ((conductor_inv + conductor_inst + conductor_access) * npv['cost_capital'])

        # get cumulative sum in millions
        prj = prj.cumsum(axis=1)/1e6

        c['prj_name'] = self.prj_name
        prj = c.join(prj)
        prj = prj.reset_index(drop=True).sort_values(by=[prj.columns[-1]])

        cost_cd = (conductor_inv + conductor_inst + conductor_access) * npv['cost_capital'] / 1e6
        cost_cd = prj[['code', 'type', 'prj_name']].join(cost_cd.cumsum(axis=1))
        
        return cost_cd

    
    def _losses_costs(self, time_horizon=100):

        c = self._get_conductors_for_cost_calc()

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)
        npv['cost_capital'] = npv.year.apply(lambda x: 1 / (1 + self.wacc)**x)

        length_m = self.length_km * 1e3          

        losses = c.losses_at_peak_mwh_per_m.apply(
                lambda r: (r + c['corona_losses_mwh_per_m'].iloc[0]) * npv['inflation']
                        * self.cost_of_losses_dol_per_mwh * length_m)

        c['prj_name'] = self.prj_name

        losses = losses * npv['cost_capital'] / 1e6
        losses = c[['code', 'type', 'prj_name']].join(losses.cumsum(axis=1))
        
        return losses

    
    def _congestion_costs(self, time_horizon=100):

        c = self._get_conductors_for_cost_calc()

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)
        npv['cost_capital'] = npv['year'].apply(lambda x: 1 / (1 + self.wacc)**x)

        congestion = c.congestion_mw.apply(lambda r: r * npv['inflation'] * 8760 * self.cost_of_congestion_dol_per_mwh)

        c['prj_name'] = self.prj_name

        congestion = congestion * npv['cost_capital'] / 1e6
        congestion = c[['code', 'type', 'prj_name']].join(congestion.cumsum(axis=1))
        
        return congestion


    def _npv(self, replace_st_at=0, replace_cd_at=0, structure_modification=False, dc=False, nbr_phases=3, st={}, time_horizon=100, consider_losses=True, filter_type=False):

        c = self._get_conductors_for_cost_calc()
            
        nbr_conds = 1 if 'nbr_conductors' not in st else st['nbr_conductors']
        str_data = st
        if str_data and 'line_angle' in str_data:
            self.cost_of_structures_unit = (str_data['str_tgt'] * str_data['str_tgt_cost']
                                        + str_data['str_ra'] * str_data['str_ra_cost']
                                        + str_data['str_nade'] * str_data['str_nade_cost']
                                        + str_data['str_ade'] * str_data['str_ade_cost']) / str_data['nbr_structures']
            self.nbr_structures = str_data['nbr_structures']

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

        npv[['structures_inv', 'conductors_inv']] = 0
        npv.loc[npv.year.isin(range(replace_st_at, time_horizon, self.structures_lifetime)), 'structures_inv'] = 1
        npv.loc[npv.year.isin(range(replace_cd_at, time_horizon, self.conductors_lifetime)), 'conductors_inv'] = 1
        npv['cost_capital'] = npv['year'].apply(lambda x: 1/(1+self.wacc)**x)

        length_kft = self.length_km * 3.28
        conductor_inv = c.dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                                                    * length_kft * self.nbr_ckts * nbr_phases * nbr_conds
        conductor_inst = c.inst_dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                                                    * length_kft * self.nbr_ckts * nbr_phases * nbr_conds
        conductor_access = c.accessories_dol_per_1000_ft.apply(lambda r: r * npv['inflation'] * npv['conductors_inv']) \
                        * length_kft * self.nbr_ckts * nbr_phases * nbr_conds

        length_m = self.length_km * 1e3

        # if not self.customize_inv_options:
        structures = c.str_costs_dol.apply(lambda r: npv['inflation'] * self.cost_of_structures_unit * npv['structures_inv'] * self.nbr_structures)
        # else:
        #     structures = c.str_costs_dol.apply(lambda r: r * npv['inflation'] * npv['structures_inv'])

        if dc:
            npv['structures_modif_inv'] = 0
            npv.at[0, 'structures_modif_inv'] = 1
            # costs of structure upgrade (if any) are added to structures costs
            structures[0] = self.cost_of_structures_modif_dol_per_unit * self.nbr_structures_modif \
                if structure_modification else structures[0]
            # costs of converters are also considered
            converters = self.cost_of_converters * npv['inflation'] * npv['structures_modif_inv']
            ss_transfo = npv['inflation'] * 0
        
        elif structure_modification:
            npv['structures_modif_inv'] = 0
            npv.at[0, 'structures_modif_inv'] = 1
            # costs of structure upgrade (if any) are added to structures costs
            structures[0] = self.cost_of_structures_modif_dol_per_unit * self.nbr_structures \
                                    if structure_modification else structures[0]
            # costs of substations and transformers modifications are also considered
            ss_transfo = self.cost_of_ss_transfo * npv['inflation'] * npv['structures_modif_inv']
            converters = npv['inflation'] * 0

        else:
            ss_transfo = npv['inflation'] * 0
            converters = npv['inflation'] * 0

        if consider_losses:
            losses = c.losses_at_peak_mwh_per_m.apply(
                lambda r: (r + c['corona_losses_mwh_per_m'].iloc[0]) * npv['inflation']
                        * self.cost_of_losses_dol_per_mwh * length_m)
        else:
            losses = c.losses_at_peak_mwh_per_m.apply(lambda r: r * npv['inflation'] * 0)

        congestion = c.congestion_mw.apply(lambda r: r * npv['inflation'] * 8760 * self.cost_of_congestion_dol_per_mwh)

        prj = ((structures + conductor_inv + conductor_inst + conductor_access + losses + ss_transfo + converters + congestion)
            * npv['cost_capital'])

        # get cumulative sum in millions
        prj = prj.cumsum(axis=1)/1e6

        c['prj_name'] = self.prj_name
        prj = c.join(prj)
        prj = prj.reset_index(drop=True).sort_values(by=[prj.columns[-1]])

        cost_st = structures * npv['cost_capital'] / 1e6
        cost_st = prj[['code', 'type', 'prj_name']].join(cost_st.cumsum(axis=1))
        cost_cd = (conductor_inv + conductor_inst + conductor_access) * npv['cost_capital'] / 1e6
        cost_cd = prj[['code', 'type', 'prj_name']].join(cost_cd.cumsum(axis=1))
        losses = losses * npv['cost_capital'] / 1e6
        losses = prj[['code', 'type', 'prj_name']].join(losses.cumsum(axis=1))
        congestion = congestion * npv['cost_capital'] / 1e6
        congestion = prj[['code', 'type', 'prj_name']].join(congestion.cumsum(axis=1))
        ss_transfo = ss_transfo * npv['cost_capital'] / 1e6
        ss_transfo = ss_transfo.cumsum()
        ss_transfo['prj_name'] = self.prj_name
        converters = converters * npv['cost_capital'] / 1e6
        converters = converters.cumsum()
        converters['prj_name'] = self.prj_name

        if filter_type:
            prj = prj.head()

        cost_cd = cost_cd.loc[cost_cd.index.isin(prj.index)]
        losses = losses.loc[losses.index.isin(prj.index)]

        return {'total_prj_perf': prj, 'cost_st': pd.DataFrame(cost_st), 'cost_cd': cost_cd, 'losses': losses,
                'cost_ss_tr': pd.DataFrame(ss_transfo), 'cost_cv': pd.DataFrame(converters), 'congestion': congestion}
        

    # ----- Main calculation methods -----
    
    def calculate_total_npv(self, time_horizon, consider_losses=False):
        
        if self.conductors_list:   
            npv = self._npv(time_horizon=time_horizon, 
                            consider_losses=consider_losses)['total_prj_perf']
            return npv
        else:
            print("Enter a list of conductors -> e.g. obj.conductors_list = [Conductor(**cond_raw)]")
            return pd.DataFrame()


    def calculate_structure_costs(self, time_horizon):

        if self.conductors_list:  
            cost = self._structure_costs(
                time_horizon=time_horizon,
                replace_st_at=self.replace_st_at    
            )
            return cost
        else:
            print("Enter a list of conductors -> e.g. obj.conductors_list = [Conductor(**cond_raw)]")
            return pd.DataFrame()


    def calculate_conductor_costs(self, time_horizon):

        if self.conductors_list:  
            cost = self._conductor_costs(
                time_horizon=time_horizon,
                replace_st_at=self.replace_st_at    
            )
            return cost
        else:
            print("Enter a list of conductors -> e.g. obj.conductors_list = [Conductor(**cond_raw)]")
            return pd.DataFrame()


    def calculate_losses_costs(self, time_horizon):

        if self.conductors_list:  
            cost = self._losses_costs(time_horizon=time_horizon)
            return cost
        else:
            print("Enter a list of conductors -> e.g. obj.conductors_list = [Conductor(**cond_raw)]")
            return pd.DataFrame()
        

    def calculate_congestion_costs(self, time_horizon):

        if self.conductors_list:  
            cost = self._congestion_costs(time_horizon=time_horizon)
            return cost
        else:
            print("Enter a list of conductors -> e.g. obj.conductors_list = [Conductor(**cond_raw)]")
            return pd.DataFrame()


class Existing(Project):

    prj_name: Optional[str] = "Existing"

    def calculate_total_npv(self, time_horizon, replace_st_at, replace_cd_at, consider_losses=False):
        
        self.time_horizon = time_horizon
        self.replace_st_at = replace_st_at
        self.replace_cd_at = replace_cd_at

        if self.conductors_list:  
            npv = self._npv(time_horizon=self.time_horizon,
                            replace_st_at=self.replace_st_at, 
                            replace_cd_at=self.replace_cd_at, 
                            consider_losses=consider_losses)['total_prj_perf']
            return npv
        else:
            return pd.DataFrame()


class Rebuild(Project):

    prj_name: str = "Rebuild"
    replace_st_at: int = 0
    replace_cd_at: int = 0


class Reconductoring(Project):
    
    prj_name: str = "Reconductoring"
    replace_cd_at: int = 0


    def calculate_total_npv(self, time_horizon, replace_st_at, consider_losses=False):
        
        self.time_horizon = time_horizon
        self.replace_st_at = replace_st_at

        if self.conductors_list:    
            npv = self._npv(time_horizon=self.time_horizon,
                            replace_st_at=self.replace_st_at,
                            consider_losses=consider_losses)['total_prj_perf']
            return npv
        else:
            return pd.DataFrame()


class VoltageUpgrade(Project):

    voltage_new_kv: float = Field(..., ge=60, description="New voltage level in case of voltage upgrade (kV)")
    structure_modification: Optional[bool] = True
    nbr_structures_modif: Optional[float] = Field(..., ge=0)
    cost_of_structure_modif_dol_per_unit: Optional[float] = Field(..., ge=0)
    cost_of_ss_transfo: Optional[float] = Field(..., ge=0)
    
    prj_name: str = "VoltageUpgrade"
    voltage_kv: float = voltage_new_kv


    # ----- Helper methods for calculations (called by the main calculation methods) -----  

    def _structure_costs(self, time_horizon=100, replace_st_at=0, st={}):

        str_data = st
        if str_data and 'line_angle' in str_data:
            self.cost_of_structures_unit = (str_data['str_tgt'] * str_data['str_tgt_cost']
                                        + str_data['str_ra'] * str_data['str_ra_cost']
                                        + str_data['str_nade'] * str_data['str_nade_cost']
                                        + str_data['str_ade'] * str_data['str_ade_cost']) / str_data['nbr_structures']
            self.nbr_structures = str_data['nbr_structures']

        c = self._get_conductors_for_cost_calc()

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

        npv[['structures_inv', 'conductors_inv']] = 0
        npv.loc[npv.year.isin(range(replace_st_at, time_horizon, self.structures_lifetime)), 'structures_inv'] = 1
        npv['cost_capital'] = npv['year'].apply(lambda x: 1 / (1 + self.wacc)**x)

        # if not self.customize_inv_options:
        structures = c.str_costs_dol.apply(lambda r: npv['inflation'] * self.cost_of_structures_unit * npv['structures_inv'] * self.nbr_structures)
        # else:
        #     structures = c.str_costs_dol.apply(lambda r: r * npv['inflation'] * npv['structures_inv'])

            
        # In case of Votage Upgrade and Reconductoring, some structures may need modifications.
        # These costs (if any) are added to structures costs
        if self.structure_modification:
            npv['structures_modif_inv'] = 0
            npv.at[0, 'structures_modif_inv'] = 1
            structures[0] = self.cost_of_structures_modif_dol_per_unit * self.nbr_structures_modif \
                if self.structure_modification else structures[0]
        
        c['prj_name'] = self.prj_name

        cost_st = structures * npv['cost_capital'] / 1e6
        cost_st = c[['code', 'type', 'prj_name']].join(cost_st.cumsum(axis=1))
        
        return cost_st


    def _substation_trasformer_costs(self, time_horizon=100):
        
        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

        npv['cost_capital'] = npv['year'].apply(lambda x: 1 / (1 + self.wacc)**x)

        npv['structures_modif_inv'] = 0
        npv.at[0, 'structures_modif_inv'] = 1
        
        # costs of substations and transformers modifications are also considered
        ss_transfo = self.cost_of_ss_transfo * npv['inflation'] * npv['structures_modif_inv']         

        ss_transfo = ss_transfo * npv['cost_capital'] / 1e6
        ss_transfo = ss_transfo.cumsum()
        ss_transfo['prj_name'] = self.prj_name

        return ss_transfo


    # ----- Main calculation methods -----

    def calculate_total_npv(self, time_horizon, replace_st_at, replace_cd_at, consider_losses=False):
        
        self.time_horizon = time_horizon
        self.replace_st_at = replace_st_at
        self.replace_cd_at = replace_cd_at

        if self.conductors_list:   
            npv = self._npv(time_horizon=self.time_horizon,
                            replace_st_at=self.replace_st_at, 
                            replace_cd_at=self.replace_cd_at,
                            structure_modification=self.structure_modification, 
                            dc=self.dc,
                            consider_losses=consider_losses)['total_prj_perf']
            return npv
        else:
            return pd.DataFrame()


    def calculate_substation_transformer_costs(self, time_horizon):
        
        self.time_horizon = time_horizon

        if self.conductors_list: 
            cost = self._substation_trasformer_costs(
                time_horizon=self.time_horizon
            )
            return cost
        else:
            return pd.DataFrame()
        

class HVDC(Project):

    voltage_new_kv: float = Field(..., ge=60, description="New voltage level in case of hvdc (kV)")
    structure_modification: Optional[bool] = False
    nbr_structures_modif: Optional[float] = Field(..., ge=0)
    cost_of_structure_modif_dol_per_unit: Optional[float] = Field(..., ge=0)
    cost_of_converters: Optional[float] = Field(..., ge=0)
    
    prj_name: str = "HVDC"
    dc: bool = True 
    nbr_phase: int = 2
    voltage_kv: float = voltage_new_kv


    # ----- Helper methods for calculations (called by the main calculation methods) -----  

    def _structure_costs(self, time_horizon=100, replace_st_at=0, st={}):

        str_data = st
        if str_data and 'line_angle' in str_data:
            self.cost_of_structures_unit = (str_data['str_tgt'] * str_data['str_tgt_cost']
                                        + str_data['str_ra'] * str_data['str_ra_cost']
                                        + str_data['str_nade'] * str_data['str_nade_cost']
                                        + str_data['str_ade'] * str_data['str_ade_cost']) / str_data['nbr_structures']
            self.nbr_structures = str_data['nbr_structures']

        c = self._get_conductors_for_cost_calc()

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

        npv[['structures_inv', 'conductors_inv']] = 0
        npv.loc[npv.year.isin(range(replace_st_at, time_horizon, self.structures_lifetime)), 'structures_inv'] = 1
        npv['cost_capital'] = npv['year'].apply(lambda x: 1 / (1 + self.wacc)**x)

        # if not self.customize_inv_options:
        structures = c.str_costs_dol.apply(lambda r: npv['inflation'] * self.cost_of_structures_unit * npv['structures_inv'] * self.nbr_structures)
        # else:
        #     structures = c.str_costs_dol.apply(lambda r: r * npv['inflation'] * npv['structures_inv'])

            
        # In case of HVDC and Reconductoring, some structures may need modifications.
        # These costs (if any) are added to structures costs
        if self.structure_modification:
            npv['structures_modif_inv'] = 0
            npv.at[0, 'structures_modif_inv'] = 1
            structures[0] = self.cost_of_structures_modif_dol_per_unit * self.nbr_structures_modif \
                if self.structure_modification else structures[0]
        
        c['prj_name'] = self.prj_name

        cost_st = structures * npv['cost_capital'] / 1e6
        cost_st = c[['code', 'type', 'prj_name']].join(cost_st.cumsum(axis=1))
        
        return cost_st


    def _converter_costs(self, time_horizon=100):

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)
        npv['cost_capital'] = npv['year'].apply(lambda x: 1 / (1 + self.wacc)**x)

        npv['structures_modif_inv'] = 0
        npv.at[0, 'structures_modif_inv'] = 1

        converters = self.cost_of_converters * npv['inflation'] * npv['structures_modif_inv']

        converters = converters * npv['cost_capital'] / 1e6
        converters = converters.cumsum()
        converters['prj_name'] = self.prj_name

        return converters
   

    # ----- Main calculation methods -----

    def calculate_total_npv(self, time_horizon, replace_st_at, replace_cd_at, consider_losses=False):
        
        self.time_horizon = time_horizon
        self.replace_st_at = replace_st_at
        self.replace_cd_at = replace_cd_at

        if self.conductors_list:   
            npv = self._npv(time_horizon=self.time_horizon,
                            replace_st_at=self.replace_st_at, 
                            replace_cd_at=self.replace_cd_at,
                            structure_modification=self.structure_modification,
                            dc=self.dc, 
                            consider_losses=consider_losses)['total_prj_perf']
            return npv
        else:
            return pd.DataFrame()


    def calculate_converter_costs(self, time_horizon):
        
        self.time_horizon = time_horizon

        if self.conductors_list:  
            cost = self._converter_costs(
                time_horizon=self.time_horizon
            )
            return cost
        else:
            return pd.DataFrame()
        
