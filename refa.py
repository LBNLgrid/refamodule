import pandas as pd
import json
from datetime import datetime
import os
from pathlib import Path
from typing import Any, List, Optional
from pydantic import ValidationError, BaseModel

from utils import load_conductors
from conductor import Conductor
from line import Line
from project import Project, Existing, Rebuild, Reconductoring, VoltageUpgrade, HVDC

class REFA(BaseModel):
    time_horizon: int
    unit_system: Optional[str] = "Imperial"
    

    def compare_projects(self, projects=List[Project], conductors_subset: List[Conductor] = {}) -> dict:
        least_cost = {}
        for prj in projects:
            least_cost[prj.prj_name] = prj.calculate_total_npv(self.time_horizon).head()

        return least_cost
























    # # -------------------------------------------------------------
    # #  Input/Output functions
    # # -------------------------------------------------------------
 
    # def save_results(self, results: dict, output_dir: str = "output_results"):
    #     """
    #     Save the results dictionary to a JSON file with a timestamped filename.
        
    #     Args:
    #         results (dict): The results to save, typically the output from comparison_prj_options.
    #         output_dir (str): Directory where the results file will be saved. Defaults to "output_results".
    #     """
    #     os.makedirs(output_dir, exist_ok=True)
    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     output_path = Path(output_dir) / f"refa_results_{timestamp}.json"
        
    #     with open(output_path, 'w') as f:
    #         json.dump(results, f, indent=4)
        
    #     print(f"Results saved to {output_path}")

    # # -------------------------------------------------------------
    # #  Getter/Setter functions for parameters using generic dotted‑path (work for any nesting level) 
    # # -------------------------------------------------------------
    
    # def get_parameter(self, dotted_path: str) -> Any:
    #     """
    #     Retrieve the value at ``dotted_path`` (e.g. "project.length_km").
    #     Raises AttributeError if the path does not exist.
    #     """
    #     parts = dotted_path.split(".")
    #     obj: Any = self._parameter_cfg
    #     for part in parts:
    #         obj = getattr(obj, part)          # may raise AttributeError automatically
    #     return obj

    # def set_parameter(self, dotted_path: str, new_value: Any) -> Line:
    #     """
    #     Update a (possibly nested) field and return the **new immutable**
    #     FullDataConfig instance. The manager stores the new instance internally.

    #     The value is validated against the field type / constraints defined
    #     in the Pydantic model. If validation fails a ``pydantic.ValidationError``
    #     bubbles up.

    #     Example:
    #         mgr.set_parameter("project.geometry.length_km", 180.0)
    #     """
    #     # Split the path – e.g. ["project", "length_km"]
    #     parts = dotted_path.split(".")
    #     if len(parts) == 1:
    #         # Top‑level field – simple case
    #         field_name = parts[0]
    #         new_cfg = self._parameter_cfg._copy_with_updates(**{field_name: new_value})
    #         self._parameter_cfg = new_cfg
    #         return new_cfg

    #     # For deeper nesting we need to rebuild the hierarchy from the leaf up to the root (copy‑on‑write).
    #     # 1️ - Pull the current dict representation (mutable)
    #     raw = self._parameter_cfg.model_dump() if hasattr(self._parameter_cfg, "model_dump") else self._parameter_cfg.dict()
    #     cur = raw
    #     for part in parts[:-1]:
    #         cur = cur[part]                     # descend; a KeyError means a bad path

    #     leaf = parts[-1]
    #     if leaf not in cur:
    #         raise AttributeError(f"Leaf '{leaf}' not found in '{'.'.join(parts[:-1])}'")
    #     cur[leaf] = new_value                     # set the new raw value

    #     # 2️ - Recreate the immutable Data from the mutated dict.
    #     try:
    #         new_cfg = FullDataConfig(**raw)           # triggers Pydantic validation
    #     except ValidationError as exc:
    #         # Re‑raise with a nice message that includes the path
    #         raise ValidationError(
    #             exc.errors(),
    #             model=FullDataConfig,
    #             loc=(dotted_path,),
    #         ) from exc

    #     # 3️ - Store the new config
    #     self._parameter_cfg = new_cfg
    #     return new_cfg

    # # -------------------------------------------------------------
    # # Convenience getters & setters for typical parameters.
    # # -------------------------------------------------------------
    
    # def get_power_mw(self) -> float:
    #     return self._parameter_cfg.project.power_mw

    # def set_power_mw(self, value: float) -> Line:
    #     self.set_parameter("project.power_mw", value)
    #     return self.get_power_mw()

    # def get_line_length_km(self) -> float:
    #     self._parameter_cfg.project.length_km
    #     return self._parameter_cfg.project.length_km

    # def set_line_length_km(self, value: float) -> Line:
    #     self.set_parameter("project.length_km", value)
    #     return self.get_line_length_km()

    # def get_cost_of_structures_unit(self) -> float:
    #     return self._parameter_cfg.economics.cost_of_structures_unit

    # def set_cost_of_structures_unit(self, value: float) -> Line:
    #     self.set_parameter("economics.cost_of_structures_unit", value)
    #     return self.get_cost_of_structures_unit()

    # def get_latitude(self) -> float:
    #     return self._parameter_cfg.environment.latitude

    # def set_latitude(self, value: float) -> Line:
    #     self.set_parameter("environment.latitude", value)
    #     return self.get_latitude()
    
    # # Parameters not unders _parameter_cfg
    # def get_time_horizon(self) -> int:
    #     return self.time_horizon

    # def set_time_horizon(self, value: int) -> int:
    #     self.time_horizon = value
    #     return self.time_horizon




# class refa_basic(dict):
#     def __init__(self, power_mw, length_km, avg_span_m, cost_of_structures_unit, latitude, elevation_m, time_horizon, unit_system="Metric"):
#         self.time_horizon = time_horizon
#         self.unit_system = unit_system
#         self.conductors = load_conductors()
#         self._line_cfg = Line.parse_file(Path("input_data_raw/parameter_cfg.json"))
#         self._line_cfg.project.power_mw = power_mw
#         self._line_cfg.project.length_km = length_km
#         self._line_cfg.project.avg_span_m = avg_span_m
#         self._line_cfg.economics.cost_of_structures_unit = cost_of_structures_unit
#         self._line_cfg.environment.latitude = latitude
#         self._line_cfg.environment.elevation_m = elevation_m

#     @property
#     def line_cfg(self) -> Line:
#         """Read‑only view of the current line config (do NOT mutate!)."""
#         return self._line_cfg


#     def compare_prj_options(self, prj_options: List[ProjectOption], cfg_overrides={}, conductors_subset: List[Conductor] = {}) -> dict:
#         """
#         Compare multiple project options using default or custom parameter configs.
        
#         Args:
#             prj_options (List[ProjectOptions]): List of ProjectOption objects to compare
#             cfg_overrides (dict): Optional dict mapping option names (str) to custom configs.
#                                  Example: {"option1": custom_cfg_1, "option2": custom_cfg_2}
#                                  Options not in this dict will use self.parameter_cfg
#             **kwargs: Additional keyword arguments (for future use)
        
#         Returns:
#             dict: Feasibility results for each project option, keyed by ProjectOption.option
#         """

#         conds_df = self.conductors.copy() if not conductors_subset else pd.DataFrame.from_records([cond.dict() for cond in conductors_subset])
#         str_strength_df = pd.DataFrame()
        
#         # Use custom config if provided (keyed by option name), otherwise use default
#         for option_key in cfg_overrides:
#             parameter_cfg = cfg_overrides[option_key].dict() if hasattr(cfg_overrides[option_key], 'dict') else cfg_overrides[option_key]
#         else:
#             parameter_cfg = self._parameter_cfg.dict()
        
#         result = {}
#         for prj_option in prj_options:         
#             prj_option_dict = prj_option.dict()
#             prj_option_dict['structures'] = {}
            
#             techn_result = get_technical_performance(conductors=conds_df, 
#                                                 prj_info=parameter_cfg['project'], 
#                                                 environment=parameter_cfg['environment'],
#                                                 loading=parameter_cfg['loading'], 
#                                                 prj_option=prj_option_dict, 
#                                                 str_strength=str_strength_df,
#                                                 include_unfeasible=False
#                                                 )
            
#             if not techn_result['performance'].empty:
#                 npv_result = npv(conductors=techn_result['performance'],
#                                 ec=parameter_cfg['economics'], 
#                                 length_km=parameter_cfg['project']['length_km'], 
#                                 prj_option=prj_option_dict,
#                                 consider_losses=bool(parameter_cfg['project']['consider_losses']), 
#                                 time_horizon=self.time_horizon, 
#                                 filter_type=False
#                                 )
#                 npv_result['conductors'] = techn_result['performance']
#                 result[prj_option.option] = {key: json.loads(df.to_json(orient='records')) for key, df in npv_result.items()}

#         return result


#     def keep_existing_line(self, existing_conductor: Conductor = {}, cfg_override={}) -> dict:
#         """
#         Evaluate the option of keeping the existing line (including the existing conductor) using default or custom parameter configs.
        
#         Args:
#             existing_conductor (Conductor): The existing conductor to evaluate
#             cfg_override (dict): Optional dict to provide custom config.
#                                  Example: {"project": {"power_mw": ...}, "economics": {"discount_rate": ...}, ...}
#                                  If prj_option.option is not in this dict, self.parameter_cfg will be used
#         Returns:
#             dict: Results for keeping the existing line, keyed by "existing"
#         """

#         parameter_cfg = cfg_override.dict() if cfg_override else self._parameter_cfg.dict() # Use custom config if provided, otherwise use default
                
#         prj_option = ProjectOption(
#             option="existing",
#             replace_st_at=parameter_cfg['economics']['structures_remaining_life'],
#             replace_cd_at=parameter_cfg['economics']['conductors_remaining_life'],
#             voltage_kv=parameter_cfg['project']['voltage_kv'],
#             structure_upgrade=False,
#             hvdc=False,
#             nbr_phases=3
#         )
#         prj_option_dict = prj_option.dict()
#         prj_option_dict['structures'] = {}
        
#         existing_conductor_df = pd.DataFrame.from_records([existing_conductor]) if existing_conductor else pd.DataFrame.from_records([parameter_cfg['existing_conductor']])

#         str_strength_df = pd.DataFrame()

#         result = {}
#         techn_result = get_technical_performance(conductors=existing_conductor_df, 
#                                         prj_info=parameter_cfg['project'], 
#                                         environment=parameter_cfg['environment'],
#                                         loading=parameter_cfg['loading'], 
#                                         prj_option=prj_option_dict, 
#                                         str_strength=str_strength_df,
#                                         include_unfeasible=True
#                                         )  
#         npv_result = npv(conductors=techn_result['performance'],
#                         ec=parameter_cfg['economics'], 
#                         length_km=parameter_cfg['project']['length_km'], 
#                         prj_option=prj_option_dict,
#                         consider_losses=bool(parameter_cfg['project']['consider_losses']),
#                         time_horizon=self.time_horizon,
#                         filter_type=False
#                         )
#         result['existing'] = {}
#         result['existing'] = {key: json.loads(df.to_json(orient='records')) for key, df in npv_result.items()}

#         return result


#     def compare_conductor_performance(self, conductors: List[Conductor], cond_specific_cfg_overrides: dict[str, Line] | None = None,
#                                       prj_option: ProjectOption | None = None,
#                                       ) -> dict:
#         """Compare conductor performance using a per‑conductor config map.

#         Args:
#             conductors: List of `Conductor` objects.
#             cond_specific_cfg_overrides: Mapping as a plain dict that will be merged with the global config for the
#                 corresponding conductor. If a `code` is missing, the global config is used.
#             prj_option: `ProjectOption` on which to compare conductor performance.
#         """

#         default_cfg = self._parameter_cfg.dict()
#         cfg_map: dict[str, dict] = {}
#         if cond_specific_cfg_overrides:
#             for code, cfg in cond_specific_cfg_overrides.items():
#                 cfg_dict = cfg.dict() if hasattr(cfg, "dict") else cfg
#                 # Per‑conductor config overrides base values
#                 cfg_map[code] = {**default_cfg, **cfg_dict}
        
#         prj_option_dict = (prj_option or self._parameter_cfg.prj_option).dict()
#         prj_option_dict['structures'] = {}
#         result = {}
        
#         for cond in conductors:
#             cfg = cfg_map.get(cond.code, default_cfg)   # fallback to global config
#             cond_df = pd.DataFrame.from_records([cond.dict()])
#             tech_result = get_technical_performance(conductors=cond_df,
#                                                    prj_info=cfg['project'],
#                                                    environment=cfg['environment'],
#                                                    loading=cfg['loading'],
#                                                    prj_option=prj_option_dict,
#                                                    str_strength=pd.DataFrame(),
#                                                    include_unfeasible=True
#                                                    )
        
#             npv_result = npv(conductors=tech_result['performance'],
#                             ec=cfg['economics'], 
#                             length_km=cfg['project']['length_km'], 
#                             prj_option=prj_option_dict,
#                             consider_losses=bool(cfg['project']['consider_losses']), 
#                             time_horizon=self.time_horizon, 
#                             filter_type=False
#                             )
            
#             result[cond.code] = {key: json.loads(df.to_json(orient='records')) for key, df in npv_result.items()}

#         return result


#     # -------------------------------------------------------------
#     #  Input/Output functions
#     # -------------------------------------------------------------
 
#     def create_conductor_spec(self, user_params: dict) -> Conductor:
#         """
#         Create a Conductor, filling missing fields with the defaults
#         from `self._parameter_cfg.existing_conductor`.

#         Args:
#             **user_params: A mapping of the fields that the caller wants to set on the new conductor.
#                         E.g. {"type": "AA", "code": "CU1/0", "area_mm2": 45.0, ...}
#         Returns:
#             Conductor: The new conductor spec with user parameters merged with defaults.
#         """
        
#         # 1️ - Grab the default conductor from the config (may be None)
#         defaults = self._parameter_cfg.existing_conductor.dict()
        
#         # 2 - Merge – user supplied values overwrite defaults
#         merged = {**defaults, **user_params}
        
#         return Conductor(**merged)

#     def create_project_option(self, user_params: dict) -> ProjectOption:
#         """
#         Create a ProjectOption, filling missing fields with defaults taken from
#         ``self._parameter_cfg`` (the current FullDataConfig).
        
#         Args:
#             **user_params: A mapping of the fields to set explicitly.
#                         E.g. {"option": "option1", "replace_st_at": 25, "replace_cd_at": 35, ...}
#         Returns:
#             ProjectOption: The new project option with user parameters merged with defaults.
#         """
        
#         # Default values pulled from the loaded configuration.
#         defaults = self._parameter_cfg.prj_option.dict()
        
#         # Merge user‑provided values – they overwrite the defaults
#         merged = {**defaults, **user_params}

#         return ProjectOption(**merged)

#     def create_full_data_config(self, user_params: dict) -> Line:
#         """
#         Create a FullDataConfig, filling missing fields with defaults taken from
#         ``self._parameter_cfg`` (the current config).
        
#         Args:
#             **user_params: A mapping of the fields to set explicitly.
#                         E.g. {"project": {"power_mw": 100.0, "length_km": 150.0, ...}, "economics": {"discount_rate": 0.05, ...}, ...}
#         Returns:
#             FullDataConfig: The new config with user parameters merged with defaults.
#         """
        
#         # Default values pulled from the loaded configuration.
#         defaults = self._parameter_cfg.dict()  
        
#         # Deep merge user‑provided values – they overwrite the defaults
#         def deep_merge(dflt, usr):
#             for key, val in usr.items():
#                 if isinstance(val, dict) and key in dflt and isinstance(dflt[key], dict):
#                     dflt[key] = deep_merge(dflt[key], val)
#                 else:
#                     dflt[key] = val
#             return dflt
        
#         merged = deep_merge(defaults, user_params)

#         return FullDataConfig(**merged)
   
#     def save_results(self, results: dict, output_dir: str = "output_results"):
#         """
#         Save the results dictionary to a JSON file with a timestamped filename.
        
#         Args:
#             results (dict): The results to save, typically the output from comparison_prj_options.
#             output_dir (str): Directory where the results file will be saved. Defaults to "output_results".
#         """
#         os.makedirs(output_dir, exist_ok=True)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         output_path = Path(output_dir) / f"refa_results_{timestamp}.json"
        
#         with open(output_path, 'w') as f:
#             json.dump(results, f, indent=4)
        
#         print(f"Results saved to {output_path}")

#     # -------------------------------------------------------------
#     #  Getter/Setter functions for parameters using generic dotted‑path (work for any nesting level) 
#     # -------------------------------------------------------------
    
#     def get_parameter(self, dotted_path: str) -> Any:
#         """
#         Retrieve the value at ``dotted_path`` (e.g. "project.length_km").
#         Raises AttributeError if the path does not exist.
#         """
#         parts = dotted_path.split(".")
#         obj: Any = self._parameter_cfg
#         for part in parts:
#             obj = getattr(obj, part)          # may raise AttributeError automatically
#         return obj

#     def set_parameter(self, dotted_path: str, new_value: Any) -> Line:
#         """
#         Update a (possibly nested) field and return the **new immutable**
#         FullDataConfig instance. The manager stores the new instance internally.

#         The value is validated against the field type / constraints defined
#         in the Pydantic model. If validation fails a ``pydantic.ValidationError``
#         bubbles up.

#         Example:
#             mgr.set_parameter("project.geometry.length_km", 180.0)
#         """
#         # Split the path – e.g. ["project", "length_km"]
#         parts = dotted_path.split(".")
#         if len(parts) == 1:
#             # Top‑level field – simple case
#             field_name = parts[0]
#             new_cfg = self._parameter_cfg._copy_with_updates(**{field_name: new_value})
#             self._parameter_cfg = new_cfg
#             return new_cfg

#         # For deeper nesting we need to rebuild the hierarchy from the leaf up to the root (copy‑on‑write).
#         # 1️ - Pull the current dict representation (mutable)
#         raw = self._parameter_cfg.model_dump() if hasattr(self._parameter_cfg, "model_dump") else self._parameter_cfg.dict()
#         cur = raw
#         for part in parts[:-1]:
#             cur = cur[part]                     # descend; a KeyError means a bad path

#         leaf = parts[-1]
#         if leaf not in cur:
#             raise AttributeError(f"Leaf '{leaf}' not found in '{'.'.join(parts[:-1])}'")
#         cur[leaf] = new_value                     # set the new raw value

#         # 2️ - Recreate the immutable Data from the mutated dict.
#         try:
#             new_cfg = FullDataConfig(**raw)           # triggers Pydantic validation
#         except ValidationError as exc:
#             # Re‑raise with a nice message that includes the path
#             raise ValidationError(
#                 exc.errors(),
#                 model=FullDataConfig,
#                 loc=(dotted_path,),
#             ) from exc

#         # 3️ - Store the new config
#         self._parameter_cfg = new_cfg
#         return new_cfg

#     # -------------------------------------------------------------
#     # Convenience getters & setters for typical parameters.
#     # -------------------------------------------------------------
    
#     def get_power_mw(self) -> float:
#         return self._parameter_cfg.project.power_mw

#     def set_power_mw(self, value: float) -> Line:
#         self.set_parameter("project.power_mw", value)
#         return self.get_power_mw()

#     def get_line_length_km(self) -> float:
#         self._parameter_cfg.project.length_km
#         return self._parameter_cfg.project.length_km

#     def set_line_length_km(self, value: float) -> Line:
#         self.set_parameter("project.length_km", value)
#         return self.get_line_length_km()

#     def get_cost_of_structures_unit(self) -> float:
#         return self._parameter_cfg.economics.cost_of_structures_unit

#     def set_cost_of_structures_unit(self, value: float) -> Line:
#         self.set_parameter("economics.cost_of_structures_unit", value)
#         return self.get_cost_of_structures_unit()

#     def get_latitude(self) -> float:
#         return self._parameter_cfg.environment.latitude

#     def set_latitude(self, value: float) -> Line:
#         self.set_parameter("environment.latitude", value)
#         return self.get_latitude()
    
#     # Parameters not unders _parameter_cfg
#     def get_time_horizon(self) -> int:
#         return self.time_horizon

#     def set_time_horizon(self, value: int) -> int:
#         self.time_horizon = value
#         return self.time_horizon
