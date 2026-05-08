from dataclasses import dataclass
import functools
import inspect
from typing import Any, Optional
import math


# ----- Parameter Getters/Setters

# CENTRALIZED PARAMETER REGISTRY (Single Source of Truth)
PARAMETER_REGISTRY = {
    # ===== CONDUCTOR MODELS =====
    'ConductorMetric': {
        'area': {
            'internal_name': 'area_mm2',
            'metric_unit': 'mm2',
            'imperial_unit': 'kcmil',
            'description': 'Conductor cross-sectional area'
        },
        'diameter': {
            'internal_name': 'diameter_mm',
            'metric_unit': 'mm',
            'imperial_unit': 'in',
            'description': 'Conductor diameter'
        },
        'weight': {
            'internal_name': 'weight_n_per_m',
            'metric_unit': 'n_per_m',
            'imperial_unit': 'lbs_per_kft',
            'description': 'Conductor weight per unit length'
        },
        'conductor_rts': {
            'internal_name': 'conductor_rts_kn',
            'metric_unit': 'kn',
            'imperial_unit': 'kip',
            'description': 'Conductor rated tensile strength'
        },
        'temp_dc': {
            'internal_name': 'temp_dc_c',
            'metric_unit': 'c',
            'imperial_unit': 'f',
            'description': 'DC temperature'
        },
        'temp_low': {
            'internal_name': 'temp_low_c',
            'metric_unit': 'c',
            'imperial_unit': 'f',
            'description': 'Low temperature'
        },
        'temp_high': {
            'internal_name': 'temp_high_c',
            'metric_unit': 'c',
            'imperial_unit': 'f',
            'description': 'High temperature'
        },
        'max_temperature': {
            'internal_name': 'max_temperature_c',
            'metric_unit': 'c',
            'imperial_unit': 'f',
            'description': 'Maximum temperature'
        },
        'res_dc': {
            'internal_name': 'res_dc_ohm_per_m',
            'metric_unit': 'ohm_per_m',
            'imperial_unit': 'ohm_per_mile',
            'description': 'DC resistance'
        },
        'res_low': {
            'internal_name': 'res_low_ohm_per_m',
            'metric_unit': 'ohm_per_m',
            'imperial_unit': 'ohm_per_mile',
            'description': 'Low temperature resistance'
        },
        'res_high': {
            'internal_name': 'res_high_ohm_per_m',
            'metric_unit': 'ohm_per_m',
            'imperial_unit': 'ohm_per_mile',
            'description': 'High temperature resistance'
        },
        'elastic_modulus': {
            'internal_name': 'elastic_modulus_gpa',
            'metric_unit': 'gpa',
            'imperial_unit': 'ksi',
            'description': 'Elastic modulus'
        },
        'coeff_thermal_expan': {
            'internal_name': 'coeff_thermal_expan_per_c',
            'metric_unit': 'per_c',
            'imperial_unit': 'per_f',
            'description': 'Thermal expansion coefficient'
        },
        'cost': {
            'internal_name': 'cost_dol_per_km',
            'metric_unit': 'dol_per_km',
            'imperial_unit': 'dol_per_kft',
            'description': 'Cost per unit length'
        },
        'installation_cost': {
            'internal_name': 'installation_dol_per_km',
            'metric_unit': 'dol_per_km',
            'imperial_unit': 'dol_per_kft',
            'description': 'Installation cost per unit length'
        },
        'accessories_cost': {
            'internal_name': 'accessories_dol_per_km',
            'metric_unit': 'dol_per_km',
            'imperial_unit': 'dol_per_kft',
            'description': 'Accessories cost per unit length'
        },
    },

    # ===== ENVIRONMENT MODELS =====
    'EnvironmentMetric': {
        'elevation': {
            'internal_name': 'elevation_m',
            'metric_unit': 'm',
            'imperial_unit': 'ft',
            'description': 'Elevation above sea level'
        },
        'wind_speed': {
            'internal_name': 'wind_speed_m_per_s',
            'metric_unit': 'm_per_s',
            'imperial_unit': 'mph',
            'description': 'Wind speed'
        },
        'ambient_temperature': {
            'internal_name': 'ambient_temperature_c',
            'metric_unit': 'c',
            'imperial_unit': 'f',
            'description': 'Ambient temperature'
        },
    },

    # ===== LINEDESIGN MODELS =====
    'LineDesignMetric': {
        'length': {
            'internal_name': 'length_km',
            'metric_unit': 'km',
            'imperial_unit': 'mile',
            'description': 'Line length'
        },
        'avg_span': {
            'internal_name': 'avg_span_m',
            'metric_unit': 'm',
            'imperial_unit': 'ft',
            'description': 'Average span'
        },
        'max_span': {
            'internal_name': 'max_span_m',
            'metric_unit': 'm',
            'imperial_unit': 'ft',
            'description': 'Maximum span'
        },
        'max_sag': {
            'internal_name': 'max_sag_m',
            'metric_unit': 'm',
            'imperial_unit': 'ft',
            'description': 'Maximum sag'
        },
    },

    # ===== LOADING MODELS =====
    'LoadingMetric': {
        'wind_ice_temperature': {
            'internal_name': 'wind_ice_temperature_c',
            'metric_unit': 'c',
            'imperial_unit': 'f',
            'description': 'Wind and ice temperature'
        },
        'pressure': {
            'internal_name': 'pressure_pa',
            'metric_unit': 'pa',
            'imperial_unit': 'lb_per_ft2',
            'description': 'Pressure'
        },
        'ice_thickness': {
            'internal_name': 'ice_thickness_m',
            'metric_unit': 'm',
            'imperial_unit': 'in',
            'description': 'Ice thickness'
        },
        'ice_density': {
            'internal_name': 'ice_density_kg_per_m3',
            'metric_unit': 'kg_per_m3',
            'imperial_unit': 'lb_per_ft3',
            'description': 'Ice density'
        },
        'additive_loading': {
            'internal_name': 'additive_loading_n_per_m',
            'metric_unit': 'n_per_m',
            'imperial_unit': 'lb_per_ft',
            'description': 'Additive loading'
        },
    },

    # ===== STRUCTURE CONFIG MODELS =====
    'StructureConfigACmetric': {
        'structure_height': {
            'internal_name': 'structure_height_m',
            'metric_unit': 'm',
            'imperial_unit': 'ft',
            'description': 'Height of representative structure'
        },
        'distance_a_b': {
            'internal_name': 'distance_a_b_m',
            'metric_unit': 'm',
            'imperial_unit': 'ft',
            'description': 'Distance between phase A and B'
        },
        'distance_a_c': {
            'internal_name': 'distance_a_c_m',
            'metric_unit': 'm',
            'imperial_unit': 'ft',
            'description': 'Distance between phase A and C'
        },
        'distance_b_c': {
            'internal_name': 'distance_b_c_m',
            'metric_unit': 'm',
            'imperial_unit': 'ft',
            'description': 'Distance between phase B and C'
        },
    },

    'StructureConfigDCmetric': {
        'structure_height': {
            'internal_name': 'structure_height_m',
            'metric_unit': 'm',
            'imperial_unit': 'ft',
            'description': 'Height of representative structure'
        },
        'distance_pos_neg_poles': {
            'internal_name': 'distance_pos_neg_poles_m',
            'metric_unit': 'm',
            'imperial_unit': 'ft',
            'description': 'Distance between positive and negative poles'
        },
    },
}


# The __init_subclass__ hook automatically injects PARAMETER_REGISTRY into models.
class ParameterAccess:
    
    # Class-level attribute to specify nested objects whose parameters should be included
    _nested_parameter_objects: list = []
    
    def __init_subclass__(cls, **kwargs):
        """Auto-inject _parameter_map from PARAMETER_REGISTRY when subclass is created."""
        super().__init_subclass__(**kwargs)
        
        class_name = cls.__name__
        if class_name in PARAMETER_REGISTRY:
            cls._parameter_map = PARAMETER_REGISTRY[class_name].copy()
        else:
            # Model not in registry - define it manually
            cls._parameter_map = {}
            # print(f"⚠️  Warning: {class_name} not found in PARAMETER_REGISTRY. "
            #       f"Please add its parameter map to PARAMETER_REGISTRY in parameter_access.py")
        
    
    @classmethod
    def get_parameter_registry_for_class(cls) -> dict:
        """Get the parameter registry entry for this model class."""
        return PARAMETER_REGISTRY.get(cls.__name__, {})
    
    @classmethod
    def get_parameters_needing_conversion(cls) -> list:
        return list(cls.get_parameter_registry_for_class().keys())
    
    @classmethod
    def get_parameter_info_static(cls, param_name: str) -> dict:
        registry = cls.get_parameter_registry_for_class()
        if param_name not in registry:
            raise ValueError(
                f"Unknown parameter '{param_name}'. "
                f"Available: {list(registry.keys())}"
            )
        return registry[param_name]
    

    # ----- helper methods

    def _resolve_nested_parameter(self, param_name: str) -> tuple:
        # Check nested objects
        for nested_name in self._nested_parameter_objects:
            if hasattr(self, nested_name):
                nested_obj = getattr(self, nested_name)
                if isinstance(nested_obj, ParameterAccess):
                    if param_name in nested_obj.list_parameters():
                        return nested_obj, param_name, True
        
        # Not found in nested objects, belongs to self
        return self, param_name, False
    
    def _get_dimensionless_fields(self) -> list:
        """Get list of model fields not in _parameter_map (dimensionless)."""
        if hasattr(self, 'model_fields'):
            all_fields = set(self.model_fields.keys())
        elif hasattr(self, '__fields__'):
            all_fields = set(self.__fields__.keys())
        else:
            all_fields = set()
        
        # Get internal field names from _parameter_map
        mapped_fields = {info['internal_name'] for info in self._parameter_map.values()}
        
        # Return fields not in the map
        return list(all_fields - mapped_fields)

    def _convert_value(self, metric_value: Any, param_info: dict, target_unit: str) -> Any:
        
        if metric_value is None:
            return None
        
        # Handle temperature conversions
        if target_unit in ('f', 'fahrenheit'):
            return math.ceil(round(metric_value * 9 / 5 + 32, 10) * 1e6) / 1e6
        elif target_unit in ('c', 'celsius'):
            return math.ceil(round(metric_value, 10) * 1e6) / 1e6
        
        # Handle thermal expansion coefficient (per degree)
        if target_unit in ('f', 'per_f'):
            return math.ceil(round(metric_value * 5 / 9, 10) * 1e6) / 1e6
        elif target_unit in ('c', 'per_c'):
            return math.ceil(round(metric_value, 10) * 1e6) / 1e6
        
        # Handle costs
        if target_unit == 'dol_per_kft':
            return math.ceil(round(metric_value * CF.ft_to_m, 10) * 1e6) / 1e6
        elif target_unit == 'dol_per_km':
            return math.ceil(round(metric_value, 10) * 1e6) / 1e6
        
        # Handle linear conversions using conversion factors
        else:
            cf_key = f"{param_info['metric_unit']}_to_{target_unit}"
            if hasattr(CF, cf_key):
                return math.ceil(round(metric_value * getattr(CF, cf_key), 10) * 1e6) / 1e6
        
        return math.ceil(round(metric_value, 10) * 1e6) / 1e6
    
    def _convert_to_metric(self, value: Any, param_info: dict, source_unit: str) -> Any:
        """Convert a value from source unit to metric for storage."""
        if value is None:
            return None
        
        # Handle temperature conversions
        if source_unit in ('f', 'fahrenheit'):
            return math.ceil(round((value - 32) * 5 / 9, 10) * 1e6) / 1e6
        elif source_unit in ('c', 'celsius'):
            return math.ceil(round(value, 10) * 1e6) / 1e6
        
        # Handle thermal expansion coefficient (per degree)
        if source_unit in ('f', 'per_f'):
            return math.ceil(round(value * 9 / 5, 10) * 1e6) / 1e6
        elif source_unit in ('c', 'per_c'):
            return math.ceil(round(value, 10) * 1e6) / 1e6
        
        # Handle costs
        if source_unit == 'dol_per_kft':
            return math.ceil(round(value * CF.m_to_ft, 10) * 1e6) / 1e6
        elif source_unit == 'dol_per_km':
            return math.ceil(round(value, 10) * 1e6) / 1e6

        # Handle linear conversions using conversion factors
        else:
            cf_key = f"{source_unit}_to_{param_info['metric_unit']}"
            if hasattr(CF, cf_key):
                return math.ceil(round(value * getattr(CF, cf_key), 10) * 1e6) / 1e6
        
        return math.ceil(round(value, 10) * 1e6) / 1e6
    

    # ----- Main methods

    def get_parameter(self, parameter_name: str, unit_system: Optional[str] = None) -> Any:
        
        if unit_system not in [None, 'metric', 'imperial']:
            raise ValueError(
                f"Unknown unit system '{unit_system}'. "
                "Available: ['metric', 'imperial']"
            )
        
        # Resolve parameter - may belong to nested object
        target_obj, resolved_param, is_nested = self._resolve_nested_parameter(parameter_name)
        if is_nested:
            return target_obj.get_parameter(resolved_param, unit_system=unit_system)
        
        if parameter_name in self._parameter_map:
            param_info = self._parameter_map[parameter_name]
            metric_field = param_info['internal_name']
            metric_value = getattr(self, metric_field)
            
            # Determine target unit
            if unit_system is None:
                target_unit = param_info['imperial_unit'] if UnitSystem.is_imperial() else param_info['metric_unit']
            else:
                target_unit = param_info[unit_system + '_unit']
            return self._convert_value(metric_value, param_info, target_unit), target_unit
        
        # Check if parameter is a direct model field (dimensionless, no conversion)
        elif hasattr(self, parameter_name):
            return getattr(self, parameter_name)
        
        else:
            raise ValueError(
                f"Unknown parameter '{parameter_name}'. "
                f"Available: {list(self._parameter_map.keys())}"
            )


    def set_parameter(self, parameter_name: str, value: Any, unit_system: Optional[str] = None) -> None:
        
        if unit_system not in [None, 'metric', 'imperial']:
            raise ValueError(
                f"Unknown unit system '{unit_system}'. "
                "Available: ['metric', 'imperial']"
            )
        
        # Resolve parameter - may belong to nested object
        target_obj, resolved_param, is_nested = self._resolve_nested_parameter(parameter_name)
        
        # If parameter belongs to nested object, delegate to it
        if is_nested:
            target_obj.set_parameter(resolved_param, value, unit_system=unit_system)
            return
        
        if parameter_name in self._parameter_map:
            param_info = self._parameter_map[parameter_name]
            metric_field = param_info['internal_name']
            
            # Determine source unit
            if unit_system is None:
                source_unit = param_info['imperial_unit'] if UnitSystem.is_imperial() else param_info['metric_unit']
            else:
                source_unit = param_info[unit_system + '_unit']
            
            # Convert to metric for storage
            metric_value = self._convert_to_metric(value, param_info, source_unit)
            setattr(self, metric_field, metric_value)
        
        elif hasattr(self, parameter_name):
            setattr(self, parameter_name, value)
        
        else:
            raise ValueError(
                f"Unknown parameter '{parameter_name}'. "
                f"Available: {list(self._parameter_map.keys())}"
            )


    def list_parameters(self) -> list:
        converted = list(self._parameter_map.keys())
        dimensionless = self._get_dimensionless_fields()

        nested_params = []
        for nested_name in self._nested_parameter_objects:
            if hasattr(self, nested_name):
                nested_obj = getattr(self, nested_name)
                if isinstance(nested_obj, ParameterAccess):
                    nested_params.extend(nested_obj.list_parameters())

        return converted + dimensionless + nested_params
    

    def get_parameter_info(self, parameter_name: str) -> dict:
        """Get information about a parameter including its units."""
        if parameter_name not in self._parameter_map:
            raise ValueError(f"Unknown parameter '{parameter_name}'")
        return self._parameter_map[parameter_name]
    

    def get_all_parameters(self, unit_system: Optional[str] = None) -> dict:
        """Get all parameters as a dictionary in the specified or current unit system."""
        result = {}
        for param_name in self.list_parameters():
            try:
                result[param_name] = self.get_parameter(param_name, unit_system=unit_system)
            except (ValueError, AttributeError):
                pass
        return result



# ---- Conversion Factors

@dataclass(frozen=True)
class _CF:

    # ── Length ────────────────────────────────────────────────────────
    m_to_mile:      float = 0.000621371
    mile_to_m:      float = 1 / 0.000621371

    km_to_mile:     float = 0.621371
    mile_to_km:     float = 1 / 0.621371

    m_to_ft:        float = 3.28084
    ft_to_m:        float = 0.3048

    m_to_in:        float = 39.3701
    in_to_m:        float = 1 / 39.3701

    mm_to_in:       float = 0.0393701
    in_to_mm:       float = 1 / 0.0393701          # 25.4

    # ── Area ──────────────────────────────────────────────────────────
    mm2_to_kcmil:   float = 1.974
    kcmil_to_mm2:   float = 1 / 1.974               # 0.5067

    # ── Mass ──────────────────────────────────────────────────────────
    kg_to_lb:       float = 2.20462
    lb_to_kg:       float = 1 / 2.20462

    # ── Linear weight (derived) ───────────────────────────────────────
    n_per_m_to_lbs_per_kft:   float = 0.225 / 0.00328084
    lbs_per_kft_to_n_per_m:   float = 0.00328084 / 0.225

    # ── Force (kN / kip) ─────────────────────────────────────────────
    kn_to_kip:      float = 0.224809
    kip_to_kn:      float = 1 / 0.224809

    # ── Pressure / Stress ─────────────────────────────────────────────
    gpa_to_ksi:     float = 145.0377378
    ksi_to_gpa:     float = 1 / 145.0377378

    pa_to_lb_per_ft2:       float = 0.020885434
    lb_per_ft2_to_pa:       float = 1 / 0.020885434

    # ── Density ───────────────────────────────────────────────────────
    kg_per_m3_to_lb_per_ft3:    float = 0.062428
    lb_per_ft3_to_kg_per_m3:    float = 1 / 0.062428

    # ── Time ──────────────────────────────────────────────────────────
    s_to_h:         float = 1 / 3600
    h_to_s:         float = 3600

    # ── Speed (derived) ───────────────────────────────────────────────
    mph_to_m_per_s: float = 0.44704
    m_per_s_to_mph: float = 1 / 0.44704

    # ── Temperature (C / F) ─────────────────────────────────────────────
    @staticmethod
    def c_to_f(v: float) -> float:  return v * 9 / 5 + 32
    @staticmethod
    def f_to_c(v: float) -> float:  return (v - 32) * 5 / 9

CF = _CF()


# ----- Unit System
import tomllib
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent / "config.toml"

def _read_config() -> str:
    """Read unit_system from config.toml at import time."""
    try:
        with open(_CONFIG_PATH, "rb") as f:
            config = tomllib.load(f)
        system = config["units"]["unit_system"]
        if system not in ("metric", "imperial"):
            raise ValueError(f"Invalid unit_system {system!r} in config.toml. Use 'metric' or 'imperial'.")
        return system
    except FileNotFoundError:
        raise FileNotFoundError(
            f"config.toml not found at {_CONFIG_PATH}. "
            f"Please create it with [units] unit_system = 'metric' or 'imperial'."
        )
    except KeyError:
        raise KeyError(
            "config.toml is missing [units] section or unit_system key. "
            "Expected format:\n\n[units]\nunit_system = 'metric'\n"
        )

class UnitSystem:
    
    _current: str = _read_config()

    @classmethod
    def set(cls, system: str) -> None:
        if system not in ("metric", "imperial"):
            raise ValueError(f"Unknown system {system!r}. Use 'metric' or 'imperial'.")
        cls._current = system
        print(f"✅ Unit system set to {system!r}")

    @classmethod
    def is_imperial(cls) -> bool:
        return cls._current == "imperial"

    @classmethod
    def is_metric(cls) -> bool:
        return cls._current == "metric"


# ----- Unit labels used when displaying results
@dataclass(frozen=True)
class _Labels:
    # ── Length ────────────────────────────────────────────────────────
    m:              str = "m"
    km:             str = "km"
    mm:             str = "mm"
    ft:             str = "ft"
    mile:           str = "mile"
    inch:           str = "in"

    # ── Temperature ───────────────────────────────────────────────────
    celsius:        str = "°C"
    fahrenheit:     str = "°F"

    # ── Speed ─────────────────────────────────────────────────────────
    m_per_s:        str = "m/s"
    mph:            str = "mph"

    # ── Area ──────────────────────────────────────────────────────────
    mm2:            str = "mm²"
    kcmil:          str = "kcmil"

    # ── Force ─────────────────────────────────────────────────────────
    n:              str = "N"
    lbs:            str = "lbs"
    kn:             str = "kN"
    kip:            str = "kip"

    # ── Linear weight ─────────────────────────────────────────────────
    n_per_m:        str = "N/m"
    lb_per_ft:      str = "lb/ft"

    # ── Pressure / Stress ─────────────────────────────────────────────
    pa:             str = "Pa"
    lb_per_ft2:     str = "lbs/ft²"
    gpa:            str = "GPa"
    ksi:            str = "ksi"
    mpsi:           str = "Mpsi"

    # ── Density ───────────────────────────────────────────────────────
    kg_per_m3:      str = "kg/m³"
    lb_per_ft3:     str = "lb/ft³"

    # ── Mass ──────────────────────────────────────────────────────────
    kg:             str = "kg"
    lb:             str = "lb"

    # ── Time ──────────────────────────────────────────────────────────
    s:              str = "s"
    h:              str = "h"

    # ── Electrical ───────────────────────────────────────────────────────
    ohm_per_m:      str = "Ω/m"
    ohm_per_mile:    str = "Ω/mile"
    kv:             str = "kV"
    a:              str = "A"
    mw:             str = "MW"
    mwh_per_m:      str = "MWh/m"
    mwh_per_mile:   str = "MWh/mile"

    # ── Dimensionless ─────────────────────────────────────────────────
    ratio:          str = "–"
    degrees:        str = "°"
    dollars:        str = "$"
    count:          str = "count"

LB = _Labels()



# ----- Validate and convert methods' user input

OPERATORS = {
    ">"  : lambda a, b: a >  b,
    ">=" : lambda a, b: a >= b,
    "<"  : lambda a, b: a <  b,
    "<=" : lambda a, b: a <= b,
    "==" : lambda a, b: a == b,
}

def param(*constraints, imperial: tuple = None, to_imperial=None):
    return {"constraints": constraints, "imperial": imperial, "to_imperial": to_imperial}

def _apply(fn_or_factor, v: float) -> float:
    return fn_or_factor(v) if callable(fn_or_factor) else v * fn_or_factor

def _apply_inv(fn_or_factor, to_imp, v: float, name: str) -> float:
    if to_imp is not None:      return _apply(to_imp, v)
    if callable(fn_or_factor):  raise ValueError(
        f"'{name}' has a callable to_si but no to_imperial provided.")
    return v / fn_or_factor

def validate_args(**param_rules: dict):
    
    for name, rule in param_rules.items():
        if not isinstance(rule, dict):
            raise TypeError(
                f"'{name}' must be wrapped in param(). "
                f"Got {type(rule).__name__}."
            )

    imperial = UnitSystem.is_imperial()

    # active_name → (met_name, to_si)  — only for imperial params
    imp_lookup = {}

    # active_name → constraints tuple in active system
    active_constraints = {}

    for met_name, rule in param_rules.items():
        raw    = rule["constraints"]
        imp    = rule["imperial"]
        to_imp = rule["to_imperial"]

        if imperial and imp is not None:
            # unpack and validate immediately so errors are obvious
            if not (isinstance(imp, tuple) and len(imp) == 2):
                raise ValueError(
                    f"'{met_name}': imperial must be (imperial_name, to_si), "
                    f"got {imp!r}"
                )
            imp_name, to_si = imp   # e.g. "max_sag_ft", CF.ft_to_m

            imp_lookup[imp_name] = (met_name, to_si)
            active_constraints[imp_name] = tuple(
                _apply_inv(to_si, to_imp, v, met_name) if i % 2 == 1 else v
                for i, v in enumerate(raw)
            )
        else:
            active_constraints[met_name] = raw

    def _to_si(k, v):
        met, to_si = imp_lookup[k]
        return met, _apply(to_si, v)

    def _validate(name, value):
        if value is None:
            return
        it = iter(active_constraints.get(name, ()))
        for op, threshold in zip(it, it):
            if op not in OPERATORS:
                raise ValueError(f"Unknown operator {op!r}. Valid: {list(OPERATORS)}")
            if not OPERATORS[op](value, threshold):
                raise ValueError(
                    f"'{name}' = {value} is out of range: must be {op} {threshold:.4g}"
                )

    def _imperial_sig(orig_sig):
        params = []
        for p in orig_sig.parameters.values():
            rule = param_rules.get(p.name)
            if rule and rule["imperial"] is not None:
                imp_name, to_si = rule["imperial"]
                default         = p.default
                if default not in (inspect.Parameter.empty, None):
                    default = _apply_inv(to_si, rule["to_imperial"], default, p.name)
                params.append(p.replace(name=imp_name, default=default))
            else:
                params.append(p)
        return orig_sig.replace(parameters=params)

    def decorator(fn):
        orig_sig   = inspect.signature(fn)
        active_sig = _imperial_sig(orig_sig) if imperial else orig_sig

        # sanity check — every active_constraints key must appear in active_sig
        sig_names = set(active_sig.parameters)
        for name in active_constraints:
            if name not in sig_names:
                raise ValueError(
                    f"validate() key '{name}' not found in {fn.__name__} signature. "
                    f"Available: {sig_names}"
                )

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if imperial:
                metric_to_imperial = {met: imp for imp, (met, _) in imp_lookup.items()}
                converted_kwargs = {}
                for k, v in kwargs.items():
                    if k in metric_to_imperial and v is not None:
                        converted_kwargs[metric_to_imperial[k]] = v
                    else:
                        converted_kwargs[k] = v
                kwargs = converted_kwargs
            
            bound = active_sig.bind(*args, **kwargs)
            bound.apply_defaults()

            for k, v in bound.arguments.items():
                _validate(k, v)

            final = (
                {(_to_si(k, v)[0] if k in imp_lookup and v is not None else k):
                 (_to_si(k, v)[1] if k in imp_lookup and v is not None else v)
                 for k, v in bound.arguments.items()}
                if imperial else
                dict(bound.arguments)
            )
            return fn(**final)

        wrapper.__signature__ = active_sig
        return wrapper

    return decorator