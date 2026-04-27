from pydantic import BaseModel, Field, model_validator
from typing import Literal, Optional, List, Dict, Union
import pandas as pd
import numpy as np

from .conductor import Conductor
from .line_design import LineDesign
from .line import Line
from .economics import Economics
from .structure_config import StructureConfig


class ProjectEssentials(BaseModel):
    # required parameters
    power_mw: float = Field(..., gt=0)
    voltage_kv: float = Field(..., ge=60)
    economics: Economics   
    
    # required (line_design + conductor_list), or line_list
    line_design: Optional[LineDesign] = None
    conductor_list: Optional[List[Conductor]] = None
    line_list: Optional[List[Line]] = None
    
    # pre-set parameters, which can be edited
    prj_name: str = "New Line"
    structure_config: StructureConfig = None
    structure_costs_specific_to_conductor: bool = False
    filter_output: bool = False


    @model_validator(mode="before")
    def _construct(cls, data):
        """Validate and construct a project with either:
        1. line_design + conductor_list (which creates line_list)
        2. line_list (which extracts line_design and conductor_list)
        
        Raises ValueError if both or neither are provided.
        """
        has_design_and_conductors = (
            data.get("line_design") is not None 
            and data.get("conductor_list") is not None
        )
        has_line_list = data.get("line_list") is not None
        
        # Check that exactly one of the two options is provided
        if not has_design_and_conductors and not has_line_list:
            raise ValueError(
                "Must provide either (line_design + conductor_list) or line_list."
            )
        if has_design_and_conductors and has_line_list:
            raise ValueError(
                "Must provide either (line_design + conductor_list) or line_list, not both"
            )
        
        # Case: line_design + conductor_list -> create line_list
        if has_design_and_conductors:
            line_design = data["line_design"]
            conductor_list = data["conductor_list"]
            data["line_list"] = [
                Line(line_design=line_design, conductor=cond) 
                for cond in conductor_list
            ]
                
        return data

    @model_validator(mode="after")
    def _ensure_unique(self):
        self.line_list = [line.model_copy(deep=True) for line in self.line_list]
        self.economics = self.economics.model_copy(deep=True)
        if self.conductor_list is not None:
            self.conductor_list = [cond.model_copy(deep=True) for cond in self.conductor_list]
            self.line_design = self.line_design.model_copy(deep=True)
        return self


    # ----- Access Economics and LineDesign parameters directly from a project
    def __getattr__(self, name):
        # Try economics first
        ec = object.__getattribute__(self, "economics")
        if hasattr(ec, name):
            return getattr(ec, name)
        
        # Try line_design next
        design = object.__getattribute__(self, "line_design")
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
        
        # If the structure_config object has this attribute, set it there
        config = getattr(self, "structure_config", None)
        if config and hasattr(config, name):
            setattr(config, name, value)
            return

        # If the line_design object has this attribute, set it there
        design = getattr(self, "line_design", None)
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
    
    def _format_line_data_for_cost_calc(self, lines):
        
        line_design = pd.DataFrame([line.line_design.model_dump() for line in lines])
        conductors = pd.DataFrame([line.conductor.model_dump() for line in lines])
        lines_df = conductors.join(line_design)
        
        lines_df = lines_df.reset_index(drop=True)
        desired_cols = line_design.columns.to_list() + \
            ['code', 'type', 'dol_per_1000_ft', 'inst_dol_per_1000_ft', 'str_costs_dol',
            'accessories_dol_per_1000_ft', 'max_temperature_c'] 
        valid_cols = lines_df.columns.intersection(desired_cols)
        lines_df = lines_df[valid_cols].copy()
        
        return lines_df
       

    def _npv(self, lines, time_horizon=100, structure_modification=False, is_hvdc=False):

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

        npv[['structures_inv', 'conductors_inv']] = 0
        npv.loc[npv.year.isin(range(self.structure_remaining_life, time_horizon, self.structures_lifetime)), 
                'structures_inv'] = 1
        npv.loc[npv.year.isin(range(self.conductor_remaining_life, time_horizon, self.conductors_lifetime)), 
                'conductors_inv'] = 1
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

        if not self.structure_costs_specific_to_conductor:
            structures = lines.apply(
                lambda r: self.cost_of_structures_dol_per_unit * r['nbr_structures'] * npv['inflation'] * npv['structures_inv'],
                axis=1
            )
        else:
            structures = lines.apply(
                lambda r: r.conductor['str_costs_dol'] * npv['inflation'] * npv['structures_inv'],
                axis=1
            )

        if is_hvdc:
            npv['structures_modif_inv'] = 0
            npv.at[0, 'structures_modif_inv'] = 1
            # costs of structure upgrade (if any) are added to structures costs
            print(structures)
            structures[0] = self.cost_structures_modif_dol_per_unit * self.nbr_structures_modif \
                if structure_modification else structures[0]
            # costs of converters are also considered
            converters = self.cost_converters_dol * npv['inflation'] * npv['structures_modif_inv']
            ss_transfo = npv['inflation'] * 0
        
        elif structure_modification:
            npv['structures_modif_inv'] = 0
            npv.at[0, 'structures_modif_inv'] = 1
            # costs of structure upgrade (if any) are added to structures costs
            structures[0] = self.cost_structures_modif_dol_per_unit * self.nbr_structures_modif \
                                    if structure_modification else structures[0]
            # costs of substations and transformers modifications are also considered
            ss_transfo = self.cost_substations_transfos_dol * npv['inflation'] * npv['structures_modif_inv']
            converters = npv['inflation'] * 0

        else:
            ss_transfo = npv['inflation'] * 0
            converters = npv['inflation'] * 0

        if 'losses_at_peak_mwh_per_m' in lines:
            losses = lines.apply(
                lambda r: (r['losses_at_peak_mwh_per_m'] + r['corona_losses_mwh_per_m']) * 
                            npv['inflation'] * r['length_km'] * 1e3 * self.cost_of_losses_dol_per_mwh,
                axis=1
            )
        else:
            losses = lines.apply(lambda _: npv['inflation'] * 0, axis=1)

        congestion = lines.congestion_mw.apply(lambda r: r * npv['inflation'] * 8760 * self.cost_of_congestion_dol_per_mwh)
        
        # Sum all costs and get cumulative sum in millions
        prj = ((structures + conductor_inv + conductor_inst + conductor_access + losses + ss_transfo + converters + congestion)
            * npv['cost_capital'])        
        
        prj = prj.cumsum(axis=1) / 1e6
        lines['prj_name'] = self.prj_name
        prj = lines.join(prj)
        prj = prj.reset_index(drop=True).sort_values(by=[prj.columns[-1]])

        if self.filter_output:
            prj = prj.head()

        return prj 


    # ----- Main calculation methods -----

    def calculate_total_npv(self, time_horizon, load_factor=None, select_feasible=True):
        
        if select_feasible:
            line_list = [line for line in self.line_list 
                         if line.is_feasible(
                            current_a=line.get_current(self.power_mw, self.voltage_kv),
                            voltage_kv=self.voltage_kv,
                            max_sag_m=line.max_sag_m,
                            structure_config=self.structure_config
                         )[0]
                        ]
        else: line_list = self.line_list
        
        if line_list:
            lines = self._format_line_data_for_cost_calc(line_list)

            if load_factor is not None:
                lines['losses_at_peak_mwh_per_m'] = [
                    line.calculate_resistive_line_losses(
                        voltage_kv=self.voltage_kv,
                        current_a=line.get_current(self.power_mw, self.voltage_kv),
                        load_factor=load_factor
                    ) for line in line_list
                ]
                lines['corona_losses_mwh_per_m'] = [
                    line.calculate_corona_discharge_losses(
                        voltage_kv=self.voltage_kv, 
                        structure_config=self.structure_config, 
                        load_factor=load_factor
                    ) for line in line_list 
                ] if self.structure_config is not None else 0

            lines['congestion_mw'] = [
                line.calculate_congestion(
                    voltage_kv=self.voltage_kv,
                    current_a=line.get_current(self.power_mw, self.voltage_kv),
                ) for line in line_list
            ]  

            npv = self._npv(
                lines=lines,
                time_horizon=time_horizon
            )

            npv['conductor'] = npv['type'] + ' ' + npv['code']
            npv = npv.rename(columns={time_horizon - 1: 'npv_total_project_costs_mill_dol'})
            
            return npv[['prj_name', 'conductor', 'npv_total_project_costs_mill_dol']]
        else:
            return pd.DataFrame()

    def calculate_structure_costs(self, time_horizon, select_feasible=True):
        
        if select_feasible:
            line_list = [line for line in self.line_list 
                         if line.is_feasible(
                            current_a=line.get_current(self.power_mw, self.voltage_kv),
                            voltage_kv=self.voltage_kv,
                            max_sag_m=line.max_sag_m,
                            structure_config=self.structure_config
                         )[0]
                        ]
        else: line_list = self.line_list

        if line_list:
            lines = self._format_line_data_for_cost_calc(line_list)
            
            npv = pd.DataFrame(columns=['year'])
            npv['year'] = list(range(time_horizon))
            npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

            npv[['structures_inv', 'conductors_inv']] = 0
            npv.loc[npv.year.isin(range(self.structure_remaining_life, time_horizon, self.structures_lifetime)), 'structures_inv'] = 1
            npv['cost_capital'] = npv.year.apply(lambda x: 1 / (1 + self.wacc)**x)

            if not self.structure_costs_specific_to_conductor:
                structures = lines.apply(
                    lambda r: self.cost_of_structures_dol_per_unit * r['nbr_structures'] * npv['inflation'] * npv['structures_inv'],
                    axis=1
                )
            else:
                structures = lines.apply(
                    lambda r: r.conductor['str_costs_dol'] * npv['inflation'] * npv['structures_inv'],
                    axis=1
                )

            lines['prj_name'] = self.prj_name

            cost_st = structures * npv['cost_capital'] / 1e6
            cost_st = lines.join(cost_st.cumsum(axis=1))
            cost_st['conductor'] = cost_st['type'] + ' ' + cost_st['code']
            cost_st = cost_st.rename(columns={time_horizon - 1: 'npv_total_structure_costs_mill_dol'})
            
            return cost_st[['prj_name', 'conductor', 'npv_total_structure_costs_mill_dol']]
        else:
            return pd.DataFrame()
    
    
    def calculate_conductor_costs(self, time_horizon, select_feasible=True):
        
        if select_feasible:
            line_list = [line for line in self.line_list 
                         if line.is_feasible(
                            current_a=line.get_current(self.power_mw, self.voltage_kv),
                            voltage_kv=self.voltage_kv,
                            max_sag_m=line.max_sag_m,
                            structure_config=self.structure_config
                         )[0]
                        ]
        else: line_list = self.line_list
        
        if line_list:

            lines = self._format_line_data_for_cost_calc(line_list)

            npv = pd.DataFrame(columns=['year'])
            npv['year'] = list(range(time_horizon))
            npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

            npv['conductors_inv'] = 0
            npv.loc[npv.year.isin(range(self.conductor_remaining_life, time_horizon, self.conductors_lifetime)), 'conductors_inv'] = 1
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

            lines['prj_name'] = self.prj_name

            cost_cd = (conductor_inv + conductor_inst + conductor_access) * npv['cost_capital'] / 1e6
            cost_cd = lines.join(cost_cd.cumsum(axis=1))
            cost_cd['conductor'] = cost_cd['type'] + ' ' + cost_cd['code']
            cost_cd = cost_cd.rename(columns={time_horizon - 1: 'npv_total_conductor_costs_mill_dol'})
            
            return cost_cd[['prj_name', 'conductor', 'npv_total_conductor_costs_mill_dol']]
        else:
            return pd.DataFrame()


    def calculate_losses_costs(self, time_horizon, load_factor, select_feasible=True):
        
        if select_feasible:
            line_list = [line for line in self.line_list 
                         if line.is_feasible(
                            current_a=line.get_current(self.power_mw, self.voltage_kv),
                            voltage_kv=self.voltage_kv,
                            max_sag_m=line.max_sag_m,
                            structure_config=self.structure_config
                         )[0]
                        ]
        else: line_list = self.line_list

        if line_list:
            lines = self._format_line_data_for_cost_calc(line_list)

            lines['losses_at_peak_mwh_per_m'] = [
                line.calculate_resistive_line_losses(
                        voltage_kv=self.voltage_kv,
                        current_a=line.get_current(self.power_mw, self.voltage_kv),
                        load_factor=load_factor
                    ) for line in line_list
            ]
            lines['corona_losses_mwh_per_m'] = [
                line.calculate_corona_discharge_losses(
                        voltage_kv=self.voltage_kv,
                        structure_config=self.structure_config, 
                        load_factor=load_factor
                    ) for line in line_list
            ] if self.structure_config is not None else 0

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
            losses['conductor'] = losses['type'] + ' ' + losses['code']
            losses = losses.rename(columns={time_horizon - 1: 'npv_total_losses_costs_mill_dol'})
            
            return losses[['prj_name', 'conductor', 'npv_total_losses_costs_mill_dol']]
        else:
            return pd.DataFrame()

    
    def calculate_congestion_costs(self, time_horizon):

        lines = self._format_line_data_for_cost_calc(self.line_list)

        lines['congestion_mw'] = [
            line.calculate_congestion(
                voltage_kv=self.voltage_kv,
                current_a=line.get_current(self.power_mw, self.voltage_kv),
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
        congestion['conductor'] = congestion['type'] + ' ' + congestion['code']
        congestion = congestion.rename(columns={time_horizon - 1: 'npv_total_congestion_costs_mill_dol'})
        
        return congestion[['prj_name', 'conductor', 'npv_total_congestion_costs_mill_dol']]


    def check_feasible_lines(self):

        result = []
        for line in self.line_list:
            result.append([
                    line.is_feasible(
                        power_mw=self.power_mw, 
                        voltage_kv=self.voltage_kv,
                        max_sag_m=line.max_span_m,
                        structure_config=self.structure_config
                    )[0], line
                ]
            )

        return result


class Existing(ProjectEssentials):
    conductor_remaining_life: int = Field(..., ge=0, 
            description="Year at which conductor replacement is planned, corresponding to conductors_remaining_life.")
    structure_remaining_life: int = Field(..., ge=0, 
            description="Year at which structure replacement is planned, corresponding to structures_remaining_life.")
    
    prj_name: str = "Existing"
        

class Rebuild(ProjectEssentials):
    structure_remaining_life: int = 0
    conductor_remaining_life: int = 0

    prj_name: str = "Rebuild"


class Reconductoring(ProjectEssentials):
    structure_remaining_life: int = Field(..., ge=0, 
            description="Year at which structure replacement is planned, corresponding to structures_remaining_life.")
    
    prj_name: str = "Reconductoring"
    conductor_remaining_life: int = 0
    

class VoltageUpgrade(ProjectEssentials):
    structure_remaining_life: int = Field(..., ge=0, 
            description="Year at which structure replacement is planned, corresponding to structures_remaining_life.")
    conductor_remaining_life: int = Field(..., ge=0, 
            description="Year at which conductor replacement is planned, corresponding to conductors_remaining_life.")
    
    
    prj_name: str = "VoltageUpgrade"

    structure_modification: bool = False
    nbr_structures_modif: float = Field(0, ge=0)
    cost_structures_modif_dol_per_unit: float = Field(50000, ge=0)
    cost_substations_transfos_dol: float = Field(0, ge=0)
    
    # ----- Main calculation methods -----

    def calculate_total_npv(self, time_horizon, load_factor=None, select_feasible=True):
        
        if select_feasible:
            line_list = [line for line in self.line_list 
                         if line.is_feasible(
                            current_a=line.get_current(self.power_mw, self.voltage_kv),
                            voltage_kv=self.voltage_kv,
                            max_sag_m=line.max_sag_m,
                            structure_config=self.structure_config
                         )[0]
                        ]
        else: line_list = self.line_list
        
        if line_list:
            lines = self._format_line_data_for_cost_calc(line_list)

            if load_factor is not None:
                lines['losses_at_peak_mwh_per_m'] = [
                    line.calculate_resistive_line_losses(
                        voltage_kv=self.voltage_kv,
                        current_a=line.get_current(self.power_mw, self.voltage_kv),
                        load_factor=load_factor
                    ) for line in line_list
                ]
                lines['corona_losses_mwh_per_m'] = [
                    line.calculate_corona_discharge_losses(
                        voltage_kv=self.voltage_kv, 
                        structure_config=self.structure_config, 
                        load_factor=load_factor
                    ) for line in line_list 
                ] if self.structure_config is not None else 0

            lines['congestion_mw'] = [
                line.calculate_congestion(
                    voltage_kv=self.voltage_kv,
                    current_a=line.get_current(self.power_mw, self.voltage_kv),
                ) for line in line_list
            ]  

            npv = self._npv(
                lines=lines,
                time_horizon=time_horizon,
                structure_modification=self.structure_modification
            )
            npv['conductor'] = npv['type'] + ' ' + npv['code']
            npv = npv.rename(columns={time_horizon - 1: 'npv_total_project_costs_mill_dol'})
            
            return npv[['prj_name', 'conductor', 'npv_total_project_costs_mill_dol']]
        else:
            return pd.DataFrame()


    def calculate_structure_costs(self, time_horizon, select_feasible=True):
        
        if select_feasible:
            line_list = [line for line in self.line_list 
                         if line.is_feasible(
                            current_a=line.get_current(self.power_mw, self.voltage_kv),
                            voltage_kv=self.voltage_kv,
                            max_sag_m=line.max_sag_m,
                            structure_config=self.structure_config
                         )[0]
                        ]
        else: line_list = self.line_list

        if line_list:
            lines = self._format_line_data_for_cost_calc(line_list)

            npv = pd.DataFrame(columns=['year'])
            npv['year'] = list(range(time_horizon))
            npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

            npv[['structures_inv', 'conductors_inv']] = 0
            npv.loc[npv.year.isin(range(self.structure_remaining_life, time_horizon, self.structures_lifetime)), 'structures_inv'] = 1
            npv['cost_capital'] = npv.year.apply(lambda x: 1 / (1 + self.wacc)**x)

            if not self.structure_costs_specific_to_conductor:
                structures = lines.apply(
                    lambda r: self.cost_of_structures_dol_per_unit * r['nbr_structures'] * npv['inflation'] * npv['structures_inv'],
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
                structures[0] = self.cost_structures_modif_dol_per_unit * self.nbr_structures_modif \
                                        if self.structure_modification else structures[0]
            
            lines['prj_name'] = self.prj_name

            cost_st = structures * npv['cost_capital'] / 1e6
            cost_st = lines.join(cost_st.cumsum(axis=1))
            cost_st['conductor'] = cost_st['type'] + ' ' + cost_st['code']
            cost_st = cost_st.rename(columns={time_horizon - 1: 'npv_total_structure_costs_mill_dol'})
            
            return cost_st[['prj_name', 'conductor', 'npv_total_structure_costs_mill_dol']]
        else:
            return pd.DataFrame()


    def calculate_substation_trasformer_costs(self, time_horizon):
        
        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

        npv['cost_capital'] = npv['year'].apply(lambda x: 1 / (1 + self.wacc)**x)

        npv['structures_modif_inv'] = 0
        npv.at[0, 'structures_modif_inv'] = 1
        
        ss_transfo = (self.cost_substations_transfos_dol * npv['inflation'] * npv['structures_modif_inv']         
                    * npv['cost_capital'] / 1e6).cumsum()
        
        ss_transfo = pd.DataFrame([ss_transfo.values], columns=npv['year'].values)
        ss_transfo['prj_name'] = self.prj_name
        ss_transfo = ss_transfo.rename(
            columns={time_horizon - 1: 'npv_total_substation_transformer_costs_mill_dol'}
        )
        
        return ss_transfo[['prj_name', 'npv_total_substation_transformer_costs_mill_dol']]


class HVDC(ProjectEssentials):
    conductor_remaining_life: int = Field(..., ge=0, 
            description="Year at which conductor replacement is planned, corresponding to conductors_remaining_life.")
    structure_remaining_life: int = Field(..., ge=0, 
            description="Year at which structure replacement is planned, corresponding to structures_remaining_life.")
    nbr_dc_poles_per_circuit: int = Field(..., ge=1, le=3)   
    
    prj_name: str = "HVDC"

    structure_modification: bool = False
    nbr_structures_modif: float = Field(0, ge=0)
    cost_structure_modif_dol_per_unit: float = Field(50000, ge=0)
    cost_converters_dol: float = Field(0, ge=0)
    
    @model_validator(mode="after")
    def _update_parameters(self):
        for line in self.line_list:
            line.line_design.nbr_bundles = self.nbr_dc_poles_per_circuit
        return self

    # ----- Main calculation methods -----

    def calculate_total_npv(self, time_horizon, load_factor=None, select_feasible=True): 
        
        if select_feasible:
            line_list = [line for line in self.line_list 
                         if line.is_feasible(
                            current_a=line.get_current(self.power_mw, self.voltage_kv, is_hvdc=True),
                            voltage_kv=self.voltage_kv,
                            max_sag_m=line.max_sag_m,
                            structure_config=self.structure_config,
                            is_hvdc=True
                         )[0]
                        ]
        else: line_list = self.line_list

        if line_list:
            lines = self._format_line_data_for_cost_calc(line_list)

            if load_factor is not None:
                lines['losses_at_peak_mwh_per_m'] = [
                    line.calculate_resistive_line_losses(
                        voltage_kv=self.voltage_kv,
                        current_a=line.get_current(self.power_mw, self.voltage_kv, is_hvdc=True),
                        load_factor=load_factor,
                        is_hvdc=True
                    ) for line in line_list
                ]
                lines['corona_losses_mwh_per_m'] = [
                    line.calculate_corona_discharge_losses(
                        voltage_kv=self.voltage_kv, 
                        structure_config=self.structure_config, 
                        load_factor=load_factor,
                        is_hvdc=True
                    ) for line in line_list 
                ] if self.structure_config is not None else 0

            lines['congestion_mw'] = [
                line.calculate_congestion(
                    voltage_kv=self.voltage_kv,
                    current_a=line.get_current(self.power_mw, self.voltage_kv, is_hvdc=True),
                    is_hvdc=True
                ) for line in line_list
            ]  
            
            npv = self._npv(
                lines=lines,
                time_horizon=time_horizon,
                structure_modification=self.structure_modification, 
                is_hvdc=True
            )
            npv['conductor'] = npv['type'] + ' ' + npv['code']
            npv = npv.rename(columns={time_horizon - 1: 'npv_total_project_costs_mill_dol'})
            
            return npv[['prj_name', 'conductor', 'npv_total_project_costs_mill_dol']]
        else:
            return pd.DataFrame()


    def calculate_structure_costs(self, time_horizon, select_feasible=True):
        
        if select_feasible:
            line_list = [line for line in self.line_list 
                         if line.is_feasible(
                            current_a=line.get_current(self.power_mw, self.voltage_kv, is_hvdc=True),
                            voltage_kv=self.voltage_kv,
                            max_sag_m=line.max_sag_m,
                            structure_config=self.structure_config,
                            is_hvdc=True
                         )[0]
                        ]
        else: line_list = self.line_list
        
        if line_list:
            lines = self._format_line_data_for_cost_calc(line_list)

            npv = pd.DataFrame(columns=['year'])
            npv['year'] = list(range(time_horizon))
            npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)

            npv[['structures_inv', 'conductors_inv']] = 0
            npv.loc[npv.year.isin(range(self.structure_remaining_life, time_horizon, self.structures_lifetime)), 'structures_inv'] = 1
            npv['cost_capital'] = npv.year.apply(lambda x: 1 / (1 + self.wacc)**x)

            if not self.structure_costs_specific_to_conductor:
                structures = lines.apply(
                    lambda r: self.cost_of_structures_dol_per_unit * r['nbr_structures'] * npv['inflation'] * npv['structures_inv'],
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
                structures[0] = self.cost_structures_modif_dol_per_unit * self.nbr_structures_modif \
                    if self.structure_modification else structures[0]
            
            lines['prj_name'] = self.prj_name

            cost_st = structures * npv['cost_capital'] / 1e6
            cost_st = lines.join(cost_st.cumsum(axis=1))
            cost_st['conductor'] = cost_st['type'] + ' ' + cost_st['code']
            cost_st = cost_st.rename(columns={time_horizon - 1: 'npv_total_structure_costs_mill_dol'})
            
            return cost_st[['prj_name', 'conductor', 'npv_total_structure_costs_mill_dol']]
        else:
            return pd.DataFrame()


    def calculate_losses_costs(self, time_horizon, load_factor, select_feasible=True):
        
        if select_feasible:
            line_list = [line for line in self.line_list 
                         if line.is_feasible(
                            current_a=line.get_current(self.power_mw, self.voltage_kv, is_hvdc=True),
                            voltage_kv=self.voltage_kv,
                            max_sag_m=line.max_sag_m,
                            structure_config=self.structure_config,
                            is_hvdc=True
                         )[0]
                        ]
        else: line_list = self.line_list

        if line_list:
            lines = self._format_line_data_for_cost_calc(line_list)

            lines['losses_at_peak_mwh_per_m'] = [
                line.calculate_resistive_line_losses(
                    voltage_kv=self.voltage_kv,
                    current_a=line.get_current(self.power_mw, self.voltage_kv, is_hvdc=True),
                    load_factor=load_factor,
                    is_hvdc=True
                ) for line in line_list
            ]
            lines['corona_losses_mwh_per_m'] = [
                line.calculate_corona_discharge_losses(
                    voltage_kv=self.voltage_kv, 
                    structure_config=self.structure_config, 
                    load_factor=load_factor,
                    is_hvdc=True
                ) for line in line_list 
            ] if self.structure_config is not None else 0

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
            losses['conductor'] = losses['type'] + ' ' + losses['code']
            losses = losses.rename(columns={time_horizon - 1: 'npv_total_losses_costs_mill_dol'})
            
            return losses[['prj_name', 'conductor', 'npv_total_losses_costs_mill_dol']]
        else:
            return pd.DataFrame()


    def calculate_congestion_costs(self, time_horizon):

        lines = self._format_line_data_for_cost_calc(self.line_list)

        lines['congestion_mw'] = [
            line.calculate_congestion(
                voltage_kv=self.voltage_kv,
                current_a=line.get_current(self.power_mw, self.voltage_kv, is_hvdc=True),
                is_hvdc=True
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
        congestion['conductor'] = congestion['type'] + ' ' + congestion['code']
        congestion = congestion.rename(columns={time_horizon - 1: 'npv_total_congestion_costs_mill_dol'})
        
        return congestion[['prj_name', 'conductor', 'npv_total_congestion_costs_mill_dol']]


    def calculate_converter_costs(self, time_horizon):

        npv = pd.DataFrame(columns=['year'])
        npv['year'] = list(range(time_horizon))
        npv['inflation'] = npv.year.apply(lambda x: (1 + self.inflation)**x)
        npv['cost_capital'] = npv['year'].apply(lambda x: 1 / (1 + self.wacc)**x)

        npv['structures_modif_inv'] = 0
        npv.at[0, 'structures_modif_inv'] = 1

        converters = (self.cost_converters_dol * npv['inflation'] * npv['structures_modif_inv']
                     * npv['cost_capital'] / 1e6).cumsum()
        
        converters = pd.DataFrame([converters.values], columns=npv['year'].values)
        converters['prj_name'] = self.prj_name
        converters = converters.rename(
            columns={time_horizon - 1: 'npv_total_converters_costs_mill_dol'}
        )

        return converters[['prj_name', 'npv_total_converters_costs_mill_dol']]


class Analysis(BaseModel):
    project_list: List[ProjectEssentials]

    def compare_project_total_costs(self, time_horizon, load_factor=None, select_feasible=True):
        """Calculate and compare total NPV for all projects in the analysis."""
        
        comparison = pd.DataFrame()
        for project in self.project_list:
            result = project.calculate_total_npv(
                time_horizon=time_horizon, 
                load_factor=load_factor, 
                select_feasible=select_feasible
            )
            comparison = pd.concat([comparison, result])

        return comparison.reset_index(drop=True)
    

    def compare_project_structure_costs(self, time_horizon, select_feasible=True):
        
        comparison = pd.DataFrame()
        for project in self.project_list:
            result = project.calculate_structure_costs(
                time_horizon=time_horizon,
                select_feasible=select_feasible
            )
            comparison = pd.concat([comparison, result])

        return comparison.reset_index(drop=True)
    

    def compare_project_conductor_costs(self, time_horizon, select_feasible=True):
        
        comparison = pd.DataFrame()
        for project in self.project_list:
            result = project.calculate_conductor_costs(
                time_horizon=time_horizon,
                select_feasible=select_feasible
            )
            comparison = pd.concat([comparison, result])

        return comparison.reset_index(drop=True)
    

    def compare_project_losses_costs(self, time_horizon, load_factor, select_feasible=True):
        
        comparison = pd.DataFrame()
        for project in self.project_list:
            result = project.calculate_losses_costs(
                time_horizon=time_horizon, 
                load_factor=load_factor, 
                select_feasible=select_feasible
            )
            comparison = pd.concat([comparison, result])

        return comparison.reset_index(drop=True)
    

    def compare_project_congestion_costs(self, time_horizon):

        comparison = pd.DataFrame()
        for project in self.project_list:
            result = project.calculate_congestion_costs(
                time_horizon=time_horizon
            )
            comparison = pd.concat([comparison, result])

        return comparison.reset_index(drop=True)