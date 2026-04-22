from pydantic import BaseModel, Field, model_validator
from typing import Literal, Optional, List, Dict
import pandas as pd
import numpy as np

from .conductor import Conductor
from .line_design import LineDesign
from .line import Line
from .economics import Economics


class Project(BaseModel):
    line_list: List[Line]
    power_mw: float = Field(..., gt=0)
    economics: Economics   
    
    replace_cd_at: int = Field(..., ge=0, description="Year at which conductor replacement is planned, corresponding to conductors_remaining_life.")
    replace_st_at: int = Field(..., ge=0, description="Year at which structure replacement is planned, corresponding to structures_remaining_life.")

    prj_name: str = "New Line"
    conductor_list: List[Conductor] = None
    shared_line_design: LineDesign = None
    
    is_hvdc: bool = False
    struct_costs_of_conductor: bool = False
    filter_output: bool = False

    
    @model_validator(mode="after")
    def _ensure_unique(self):
        self.line_list = [line.model_copy(deep=True) for line in self.line_list]
        self.economics = self.economics.model_copy(deep=True)
        return self

    # ----- SCENARIO: Initialize with a list of conductors and a shared line design
    @classmethod
    def from_shared_line_design( cls, conductor_list: List[Conductor], line_design: LineDesign,
        economics: Economics, power_mw: float, replace_st_at: int, replace_cd_at: int, **kwargs):
        """Create project from shared line design with all optional parameters delegated to defaults.
        Args:
            conductor_list: List of conductors to use
            line_design: Shared line design for all conductors
            economics: Economics object
            power_mw: Power in MW
            replace_st_at: Year to replace structures
            replace_cd_at: Year to replace conductors
            **kwargs: Additional optional parameters (prj_name, is_hvdc, etc.)
        """
        lines = [Line(line_design=line_design, conductor=cond) for cond in conductor_list]
        return cls(
            line_list=lines,
            conductor_list=[cond.model_copy(deep=True) for cond in conductor_list],  # Store copies to ensure uniqueness
            shared_line_design=line_design.model_copy(deep=True),
            economics=economics.model_copy(deep=True),  
            power_mw=power_mw,
            replace_st_at=replace_st_at,
            replace_cd_at=replace_cd_at,
            **kwargs  # Pass any additional parameters
        )


    # ----- Access Economics and LineDesign parameters directly from Project
    def __getattr__(self, name):
        # Try economics first
        ec = object.__getattribute__(self, "economics")
        if hasattr(ec, name):
            return getattr(ec, name)
        
        # Try shared_line_design next
        design = object.__getattribute__(self, "shared_line_design")
        if hasattr(design, name):
            return getattr(design, name)
        
        raise AttributeError(f"{type(self).__name__!r} has no attribute {name!r}")


    def __setattr__(self, name, value):
        # If it's a defined field of Project, use standard Pydantic setting
        if name in type(self).model_fields:
            super().__setattr__(name, value)
            return

        # If the economics object has this attribute, set it there
        ec = getattr(self, "economics", None)
        if ec and hasattr(ec, name):
            setattr(ec, name, value)
            return

        # If the shared_line_design object has this attribute, set it there
        design = getattr(self, "shared_line_design", None)
        env = getattr(self, "environment", None)
        if (design and hasattr(design, name)) and not hasattr(env, name):
            setattr(design, name, value)
            return 
        
        # If the environment object has this attribute, set it there
        if env and hasattr(env, name):
            setattr(env, name, value)
            return
        
        # Fallback to default behavior
        super().__setattr__(name, value)


    # ----- Internal calculation methods (called by the main calculation methods) -----    
    
    def _format_line_data_for_cost_calc(self):
        
        line_design = pd.DataFrame([line.line_design.model_dump() for line in self.line_list])
        conductors = pd.DataFrame([line.conductor.model_dump() for line in self.line_list])
        lines = conductors.join(line_design)
        
        lines = lines.reset_index(drop=True)
        desired_cols = line_design.columns.to_list() + \
            ['code', 'type', 'dol_per_1000_ft', 'inst_dol_per_1000_ft', 'str_costs_dol',
            'accessories_dol_per_1000_ft', 'max_temperature_c'] 
        valid_cols = lines.columns.intersection(desired_cols)
        lines = lines[valid_cols].copy()
        
        return lines
       

    def _npv(self, time_horizon=100, structure_modification=False, load_factor=None, 
            structure_config=None):

        lines = self._format_line_data_for_cost_calc()

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

        npv[['structures_inv', 'conductors_inv']] = 0
        npv.loc[npv.year.isin(range(self.replace_st_at, time_horizon, self.structures_lifetime)), 'structures_inv'] = 1
        npv.loc[npv.year.isin(range(self.replace_cd_at, time_horizon, self.conductors_lifetime)), 'conductors_inv'] = 1
        npv['cost_capital'] = npv['year'].apply(lambda x: 1 / (1 + self.wacc)**x)

        conductor_inv = lines.apply(
            lambda r: r['dol_per_1000_ft'] * npv['inflation'] * npv['conductors_inv'] * r['length_km'] * 3.28 *
                r['nbr_circuits'] * r['nbr_bundles'] * r['nbr_conds_per_bundle'],
            axis=1
        )
        conductor_inst = lines.apply(
            lambda r: r['inst_dol_per_1000_ft'] * npv['inflation'] * npv['conductors_inv'] * r['length_km'] * 3.28 *
                r['nbr_circuits'] * r['nbr_bundles'] * r['nbr_conds_per_bundle'],
            axis=1
        )
        conductor_access = lines.apply(
            lambda r: r['accessories_dol_per_1000_ft'] * npv['inflation'] * npv['conductors_inv'] * r['length_km'] * 3.28 *
                r['nbr_circuits'] * r['nbr_bundles'] * r['nbr_conds_per_bundle'],
            axis=1
        )

        if not self.struct_costs_of_conductor:
            structures = lines.apply(
                lambda r: self.cost_of_structures_unit * r['nbr_structures'] * npv['inflation'] * npv['structures_inv'],
                axis=1
            )
        else:
            structures = lines.apply(
                lambda r: r.conductor['str_costs_dol'] * npv['inflation'] * npv['structures_inv'],
                axis=1
            )

        if self.is_hvdc:
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
            structures[0] = self.cost_of_structures_modif_dol_per_unit * lines.nbr_structures \
                                    if structure_modification else structures[0]
            # costs of substations and transformers modifications are also considered
            ss_transfo = self.cost_of_ss_transfo * npv['inflation'] * npv['structures_modif_inv']
            converters = npv['inflation'] * 0

        else:
            ss_transfo = npv['inflation'] * 0
            converters = npv['inflation'] * 0

        if load_factor is not None:
            lines['losses_at_peak_mwh_per_m'] = [
                line.calculate_resistive_line_losses(
                    current_a=line.get_peak_current(power_mw=self.power_mw, is_hvdc=self.is_hvdc),
                    load_factor=load_factor, 
                    is_hvdc=self.is_hvdc) for line in self.line_list
            ]
            lines['corona_losses_mwh_per_m'] = [
                line.calculate_corona_discharge_losses(
                    environment=line.environment, 
                    structure_config=structure_config, 
                    load_factor=load_factor, 
                    is_hvdc=self.is_hvdc) for line in self.line_list 
            ] if structure_config is not None else 0
            
            losses = lines.apply(
                lambda r: (r['losses_at_peak_mwh_per_m'] + r['corona_losses_mwh_per_m']) * 
                            npv['inflation'] * r['length_km'] * 1e3 * self.cost_of_losses_dol_per_mwh,
                axis=1
            )
        else:
            losses = lines.apply(lambda _: npv['inflation'] * 0, axis=1)

        lines['congestion_mw'] = [
            line.calculate_congestion(
                current_a=line.get_peak_current(power_mw=self.power_mw, is_hvdc=self.is_hvdc),
                is_hvdc=self.is_hvdc
            ) for line in self.line_list
        ]
        congestion = lines.congestion_mw.apply(lambda r: r * npv['inflation'] * 8760 * self.cost_of_congestion_dol_per_mwh)
        
        # Sum all costs and get cumulative sum in millions
        prj = ((structures + conductor_inv + conductor_inst + conductor_access + losses + ss_transfo + converters + congestion)
            * npv['cost_capital'])        
        
        prj = prj.cumsum(axis=1)/1e6
        lines['prj_name'] = self.prj_name
        prj = lines.join(prj)
        prj = prj.reset_index(drop=True).sort_values(by=[prj.columns[-1]])

        if self.filter_output:
            prj = prj.head()

        return prj
        

    # ----- Main calculation methods -----

    def calculate_total_npv(self, time_horizon, load_factor=None, structure_config=None):
          
        npv = self._npv(time_horizon=time_horizon, 
                        load_factor=load_factor, 
                        structure_config=structure_config)
        
        return npv


    def calculate_structure_costs(self, time_horizon):

        lines = self._format_line_data_for_cost_calc()

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

        npv[['structures_inv', 'conductors_inv']] = 0
        npv.loc[npv.year.isin(range(self.replace_st_at, time_horizon, self.structures_lifetime)), 'structures_inv'] = 1
        npv['cost_capital'] = npv.year.apply(lambda x: 1 / (1 + self.wacc)**x)

        if not self.struct_costs_of_conductor:
            structures = lines.apply(
                lambda r: self.cost_of_structures_unit * r['nbr_structures'] * npv['inflation'] * npv['structures_inv'],
                axis=1
            )
        else:
            structures = lines.apply(
                lambda r: r.conductor['str_costs_dol'] * npv['inflation'] * npv['structures_inv'],
                axis=1
            )

        lines['prj_name'] = self.prj_name

        cost_st = structures * npv['cost_capital'] / 1e6
        cost_st = lines[['code', 'type', 'prj_name']].join(cost_st.cumsum(axis=1))
        
        return cost_st
    
    
    def calculate_conductor_costs(self, time_horizon):

        lines = self._format_line_data_for_cost_calc()

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

        npv['conductors_inv'] = 0
        npv.loc[npv.year.isin(range(self.replace_cd_at, time_horizon, self.conductors_lifetime)), 'conductors_inv'] = 1
        npv['cost_capital'] = npv['year'].apply(lambda x: 1 / (1 + self.wacc)**x)

        conductor_inv = lines.apply(
            lambda r: r['dol_per_1000_ft'] * npv['inflation'] * npv['conductors_inv'] *r['length_km'] * 3.28 *
                r['nbr_circuits'] * r['nbr_bundles'] * r['nbr_conds_per_bundle'],
            axis=1
        )
        conductor_inst = lines.apply(
            lambda r: r['inst_dol_per_1000_ft'] * npv['inflation'] * npv['conductors_inv'] * r['length_km'] * 3.28 *
                r['nbr_circuits'] * r['nbr_bundles'] * r['nbr_conds_per_bundle'],
            axis=1
        )
        conductor_access = lines.apply(
            lambda r: r['accessories_dol_per_1000_ft'] * npv['inflation'] * npv['conductors_inv'] * r['length_km'] * 3.28 *
                r['nbr_circuits'] * r['nbr_bundles'] * r['nbr_conds_per_bundle'],
            axis=1
        )

        prj = ((conductor_inv + conductor_inst + conductor_access) * npv['cost_capital'])

        # get cumulative sum in millions
        prj = prj.cumsum(axis=1)/1e6

        lines['prj_name'] = self.prj_name
        prj = lines.join(prj)
        prj = prj.reset_index(drop=True).sort_values(by=[prj.columns[-1]])

        cost_cd = (conductor_inv + conductor_inst + conductor_access) * npv['cost_capital'] / 1e6
        cost_cd = prj[['code', 'type', 'prj_name']].join(cost_cd.cumsum(axis=1))
        
        return cost_cd

    
    def calculate_losses_costs(self, time_horizon, load_factor, structure_config=None):

        lines = self._format_line_data_for_cost_calc()
        lines['losses_at_peak_mwh_per_m'] = [
            line.calculate_resistive_line_losses(
                    current_a=line.get_peak_current(power_mw=self.power_mw, is_hvdc=self.is_hvdc),
                    load_factor=load_factor, is_hvdc=self.is_hvdc) for line in self.line_list
        ]
        lines['corona_losses_mwh_per_m'] = [
            line.calculate_corona_discharge_losses(
                    environment=line.environment, structure_config=structure_config, 
                    load_factor=load_factor, is_hvdc=self.is_hvdc) for line in self.line_list
        ] if structure_config is not None else 0

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)
        npv['cost_capital'] = npv.year.apply(lambda x: 1 / (1 + self.wacc)**x)

        losses = lines.apply(
            lambda r: (r['losses_at_peak_mwh_per_m'] + r['corona_losses_mwh_per_m']) *
                npv['inflation'] * self.cost_of_losses_dol_per_mwh * r['length_km'] * 1e3,
            axis=1
        )

        lines['prj_name'] = self.prj_name

        losses = losses * npv['cost_capital'] / 1e6
        losses = lines[['code', 'type', 'prj_name']].join(losses.cumsum(axis=1))
        
        return losses

    
    def calculate_congestion_costs(self, time_horizon):

        lines = self._format_line_data_for_cost_calc()
        lines['congestion_mw'] = [
            line.calculate_congestion(
                current_a=line.get_peak_current(power_mw=self.power_mw, is_hvdc=self.is_hvdc),
                is_hvdc=self.is_hvdc
            ) for line in self.line_list
        ]

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)
        npv['cost_capital'] = npv['year'].apply(lambda x: 1 / (1 + self.wacc)**x)

        congestion = lines.congestion_mw.apply(
            lambda r: r * npv['inflation'] * 8760 * self.cost_of_congestion_dol_per_mwh
        )

        lines['prj_name'] = self.prj_name

        congestion = congestion * npv['cost_capital'] / 1e6
        congestion = lines[['code', 'type', 'prj_name']].join(congestion.cumsum(axis=1))
        
        return congestion


class Existing(Project):
    prj_name: str = "Existing"
        

class Rebuild(Project):
    prj_name: str = "Rebuild"
    replace_st_at: int = 0
    replace_cd_at: int = 0


class Reconductoring(Project):
    prj_name: str = "Reconductoring"
    replace_cd_at: int = 0
       

class VoltageUpgrade(Project):
    prj_name: str = "VoltageUpgrade"

    voltage_new_kv: float = Field(..., ge=60, description="New voltage level in case of voltage upgrade (kV)")
    
    structure_modification: bool = False
    nbr_structures_modif: float = Field(0, ge=0)
    cost_of_structure_modif_dol_per_unit: float = Field(50000, ge=0)
    cost_of_ss_transfo: float = Field(0, ge=0)
    
    @model_validator(mode='after')
    def _update_parameters(self):
        for line in self.line_list:
            line.line_design.voltage_kv = self.voltage_new_kv
        return self

    # ----- Main calculation methods -----

    def calculate_total_npv(self, time_horizon, load_factor=None, structure_config=None):   
        npv = self._npv(time_horizon=time_horizon,
                        structure_modification=self.structure_modification, 
                        load_factor=load_factor,
                        structure_config=structure_config
                        )
        
        return npv


    def calculate_structure_costs(self, time_horizon):

        lines = self._format_line_data_for_cost_calc()

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

        npv[['structures_inv', 'conductors_inv']] = 0
        npv.loc[npv.year.isin(range(self.replace_st_at, time_horizon, self.structures_lifetime)), 'structures_inv'] = 1
        npv['cost_capital'] = npv.year.apply(lambda x: 1 / (1 + self.wacc)**x)

        if not self.struct_costs_of_conductor:
            structures = lines.apply(
                lambda r: self.cost_of_structures_unit * r['nbr_structures'] * npv['inflation'] * npv['structures_inv'],
                axis=1
            )
        else:
            structures = lines.apply(
                lambda r: r.conductor['str_costs_dol'] * npv['inflation'] * npv['structures_inv'],
                axis=1
            )
        
        # In case of Votage Upgrade and Reconductoring, some structures may need modifications.
        # These costs (if any) are added to structures costs
        if self.structure_modification:
            npv['structures_modif_inv'] = 0
            npv.at[0, 'structures_modif_inv'] = 1
            structures[0] = self.cost_of_structures_modif_dol_per_unit * self.nbr_structures_modif \
                                    if self.structure_modification else structures[0]
        
        lines['prj_name'] = self.prj_name

        cost_st = structures * npv['cost_capital'] / 1e6
        cost_st = lines[['code', 'type', 'prj_name']].join(cost_st.cumsum(axis=1))
        
        return cost_st


    def calculate_substation_trasformer_costs(self, time_horizon):
        
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


class HVDC(Project):
    prj_name: str = "HVDC"

    voltage_new_kv: float = Field(..., ge=60, description="New voltage level in case of hvdc (kV)")

    structure_modification: bool = False
    nbr_structures_modif: float = Field(0, ge=0)
    cost_of_structure_modif_dol_per_unit: float = Field(50000, ge=0)
    cost_of_converters: float = Field(0, ge=0)
    
    is_hvdc: bool = True
 
    @model_validator(mode='after')
    def _update_parameters(self):
        """Set voltage_kv from voltage_new_kv and nbr_bundles from nbr_dc_poles after object creation."""
        for line in self.line_list:
            line.line_design.voltage_kv = self.voltage_new_kv
        return self

    # ----- Main calculation methods -----

    def calculate_total_npv(self, time_horizon, load_factor=None, structure_config=None): 
        npv = self._npv(time_horizon=time_horizon,
                        structure_modification=self.structure_modification, 
                        load_factor=load_factor,
                        structure_config=structure_config
                        )
        
        return npv
    

    def calculate_structure_costs(self, time_horizon):
        
        lines = self._format_line_data_for_cost_calc()

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

        npv[['structures_inv', 'conductors_inv']] = 0
        npv.loc[npv.year.isin(range(self.replace_st_at, time_horizon, self.structures_lifetime)), 'structures_inv'] = 1
        npv['cost_capital'] = npv.year.apply(lambda x: 1 / (1 + self.wacc)**x)

        if not self.struct_costs_of_conductor:
            structures = lines.apply(
                lambda r: self.cost_of_structures_unit * r['nbr_structures'] * npv['inflation'] * npv['structures_inv'],
                axis=1
            )
        else:
            structures = lines.apply(
                lambda r: r.conductor['str_costs_dol'] * npv['inflation'] * npv['structures_inv'],
                axis=1
            )

        # In case of Votage Upgrade and Reconductoring, some structures may need modifications.
        # These costs (if any) are added to structures costs
        if self.structure_modification:
            npv['structures_modif_inv'] = 0
            npv.at[0, 'structures_modif_inv'] = 1
            structures[0] = self.cost_of_structures_modif_dol_per_unit * self.nbr_structures_modif \
                if self.structure_modification else structures[0]
        
        lines['prj_name'] = self.prj_name

        cost_st = structures * npv['cost_capital'] / 1e6
        cost_st = lines[['code', 'type', 'prj_name']].join(cost_st.cumsum(axis=1))
        
        return cost_st


    def calculate_converter_costs(self, time_horizon):

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


class Analysis(BaseModel):
    list_of_projects: List[Project]

    def compare_project_total_costs(self, time_horizon, load_factor=None, structure_config=None):
        """Calculate and compare total NPV for all projects in the analysis."""
        comparison = pd.DataFrame()
        for project in self.list_of_projects:
            result = project.calculate_total_npv(
                time_horizon=time_horizon, load_factor=load_factor, structure_config=structure_config
                )[['prj_name', 'type', 'code', time_horizon - 1]]
            result['conductor'] = result['type'] + ' ' + result['code']
            result = result.rename(columns={time_horizon - 1: 'npv_total_project_costs_mill_dol'})
            comparison = pd.concat([comparison, result[['prj_name', 'conductor', 'npv_total_project_costs_mill_dol']]])

        return comparison.reset_index(drop=True)
    

    def compare_project_structure_costs(self, time_horizon):
        comparison = pd.DataFrame()
        for project in self.list_of_projects:
            result = project.calculate_structure_costs(
                time_horizon=time_horizon
                )[['prj_name', 'type', 'code', time_horizon - 1]]
            result['conductor'] = result['type'] + ' ' + result['code']
            result = result.rename(columns={time_horizon - 1: 'npv_total_structure_costs_mill_dol'})
            comparison = pd.concat([comparison, result[['prj_name', 'conductor', 'npv_total_structure_costs_mill_dol']]])

        return comparison.reset_index(drop=True)
    

    def compare_project_conductor_costs(self, time_horizon):
        comparison = pd.DataFrame()
        for project in self.list_of_projects:
            result = project.calculate_conductor_costs(
                time_horizon=time_horizon
                )[['prj_name', 'type', 'code', time_horizon - 1]]
            result['conductor'] = result['type'] + ' ' + result['code']
            result = result.rename(columns={time_horizon - 1: 'npv_total_conductor_costs_mill_dol'})
            comparison = pd.concat([comparison, result[['prj_name', 'conductor', 'npv_total_conductor_costs_mill_dol']]])

        return comparison.reset_index(drop=True)
    

    def compare_project_losses_costs(self, time_horizon, load_factor, structure_config=None):
        comparison = pd.DataFrame()
        for project in self.list_of_projects:
            result = project.calculate_losses_costs(
                time_horizon=time_horizon, load_factor=load_factor, structure_config=structure_config
                )[['prj_name', 'type', 'code', time_horizon - 1]]
            result['conductor'] = result['type'] + ' ' + result['code']
            result = result.rename(columns={time_horizon - 1: 'npv_total_losses_costs_mill_dol'})
            comparison = pd.concat([comparison, result[['prj_name', 'conductor', 'npv_total_losses_costs_mill_dol']]])

        return comparison.reset_index(drop=True)
    

    def compare_project_congestion_costs(self, time_horizon):
        comparison = pd.DataFrame()
        for project in self.list_of_projects:
            result = project.calculate_congestion_costs(
                time_horizon=time_horizon
                )[['prj_name', 'type', 'code', time_horizon - 1]]
            result['conductor'] = result['type'] + ' ' + result['code']
            result = result.rename(columns={time_horizon - 1: 'npv_total_congestion_costs_mill_dol'})
            comparison = pd.concat([comparison, result[['prj_name', 'conductor', 'npv_total_congestion_costs_mill_dol']]])

        return comparison.reset_index(drop=True)