# Parameter Unit System Overview

## Introduction

The REFA module implements a comprehensive unit conversion system using three key objects:
- **`UnitSystem`**: Definition of the unit system to be used for input/output interaction with the module
- **`CF` (Conversion Factors)**: Numerical conversion factors between metric and imperial units
- **`LB` (Labels)**: Human-readable unit labels for display in results

This document explains how these are used throughout the codebase for seamless metric/imperial interoperability.

## UnitSystem

The `UnitSystem` class provides a global mechanism for managing the active unit system throughout the REFA module. It acts as a singleton that controls which unit system is used for all parameter conversions, function signatures, and user-facing outputs.

## Purpose

`UnitSystem` serves as the single source of truth for:
1. **Active unit system** - Whether the module operates in metric or imperial mode
2. **Configuration persistence** - Reading the default unit system from `config.toml`
4. **Global state** - Ensuring all components use the same unit system

## Definition

Located in `refa/system_parameters/parameter_access.py`

## Core Methods

### `is_imperial()`

Checks if the current unit system is imperial.

**Returns:**
- `bool` - `True` if in imperial mode, `False` otherwise

### `is_metric()`

Checks if the current unit system is metric.

**Returns:**
- `bool` - `True` if in metric mode, `False` otherwise


## Configuration File

The default unit system is read from `refa/system_parameters/config.toml`:

```toml
[units]
unit_system = "metric"  # or "imperial"
```

### `set(system)`

Sets the active unit system globally. 
The new system will be effective only when all imported models from REFA module are reloaded. Therefore, the recommended way to change the system of units is to directly update `config.toml` file before any imports. 

**Parameters:**
- `system` (str): Target unit system - `'metric'` or `'imperial'`

**Raises:**
- `ValueError` if system is not `'metric'` or `'imperial'`


## Conversion Factors (CF)

### Purpose

`CF` is a frozen dataclass containing all conversion factors needed to convert between metric and imperial units. It serves as the single source of truth for all unit conversions.

### Definition

Located in `refa/system_parameters/parameter_access.py`:

```python
@dataclass(frozen=True)
class _CF:
    # Length conversions
    m_to_mile: float = 0.000621371
    mile_to_m: float = 1 / 0.000621371
    km_to_mile: float = 0.621371
    mile_to_km: float = 1 / 0.621371
    m_to_ft: float = 3.28084
    ft_to_m: float = 0.3048
    # ... and many more
    
    # Temperature conversions (functions)
    @staticmethod
    def c_to_f(v: float) -> float:
        return v * 9 / 5 + 32
    
    @staticmethod
    def f_to_c(v: float) -> float:
        return (v - 32) * 5 / 9

CF = _CF()  # Singleton instance
```

### Available Conversion Factors

#### Length
```python
CF.m_to_mile        # 0.000621371
CF.mile_to_m        # 1609.344
CF.km_to_mile       # 0.621371
CF.mile_to_km       # 1.60934
CF.m_to_ft          # 3.28084
CF.ft_to_m          # 0.3048
CF.m_to_in          # 39.3701
CF.in_to_m          # 0.0254
CF.mm_to_in         # 0.0393701
CF.in_to_mm         # 25.4
```

#### Area
```python
CF.mm2_to_kcmil     # 1.974
CF.kcmil_to_mm2     # 0.5067
```

#### Mass & Weight
```python
CF.kg_to_lb         # 2.20462
CF.lb_to_kg         # 0.453592
CF.n_per_m_to_lbs_per_kft  # 0.0685
CF.lbs_per_kft_to_n_per_m  # 14.593
```

#### Force
```python
CF.kn_to_kip        # 0.224809
CF.kip_to_kn        # 4.44822
```

#### Pressure & Stress
```python
CF.gpa_to_ksi       # 145.0377378
CF.ksi_to_gpa       # 0.00689476
CF.pa_to_lb_per_ft2 # 0.020885434
CF.lb_per_ft2_to_pa # 47.8803
```

#### Density
```python
CF.kg_per_m3_to_lb_per_ft3  # 0.062428
CF.lb_per_ft3_to_kg_per_m3  # 16.0185
```

#### Speed
```python
CF.mph_to_m_per_s   # 0.44704
CF.m_per_s_to_mph   # 2.23694
```

#### Temperature (Functions)
```python
CF.c_to_f(celsius_value)    # Convert Celsius to Fahrenheit
CF.f_to_c(fahrenheit_value) # Convert Fahrenheit to Celsius
```

### Usage in Parameter Access

The `ParameterAccess` class uses `CF` internally for automatic conversions:

```python
def _convert_value(self, metric_value: Any, param_info: dict, target_unit: str) -> Any:
    """Convert metric value to target unit using CF."""
    
    # Special handling for temperature
    if target_unit in ('f', 'fahrenheit'):
        return CF.c_to_f(metric_value)
    
    # Special handling for costs
    if target_unit == 'dol_per_kft':
        return metric_value * CF.ft_to_m
    
    # General linear conversions
    cf_key = f"{param_info['metric_unit']}_to_{target_unit}"
    if hasattr(CF, cf_key):
        return metric_value * getattr(CF, cf_key)
```

### Usage in validate_args Decorator

The `validate_args` decorator uses `CF` for imperial parameter conversion:

```python
@validate_args(
    max_sag_m=param(
        ">", 0,
        imperial=("max_sag_ft", CF.ft_to_m),  # Imperial name and conversion
        to_imperial=CF.m_to_ft                 # Reverse conversion for display
    )
)
def is_sag_feasible(self, max_sag_m, ...):
    # When in imperial mode, user passes max_sag_ft
    # Decorator converts to max_sag_m using CF.ft_to_m
    pass
```

Method `param()` in `parameter_access.py` helps formatting validation and conversion rules for each considedred parameter.

## Unit Labels (LB)

### Purpose

`LB` is a frozen dataclass containing human-readable labels for all units. These are used when displaying results to users.

### Definition

Located in `refa/system_parameters/parameter_access.py`:

```python
@dataclass(frozen=True)
class _Labels:
    # Length
    m: str = "m"
    km: str = "km"
    mm: str = "mm"
    ft: str = "ft"
    mile: str = "mile"
    inch: str = "in"
    
    # Temperature
    celsius: str = "°C"
    fahrenheit: str = "°F"
    
    # Area
    mm2: str = "mm²"
    kcmil: str = "kcmil"
    
    # Force
    kn: str = "kN"
    kip: str = "kip"
    
    # ... and many more

LB = _Labels()  # Singleton instance
```

### Available Labels

#### Length
```python
LB.m        # "m"
LB.km       # "km"
LB.mm       # "mm"
LB.ft       # "ft"
LB.mile     # "mile"
LB.inch     # "in"
```

#### Temperature
```python
LB.celsius      # "°C"
LB.fahrenheit   # "°F"
```

#### Speed
```python
LB.m_per_s      # "m/s"
LB.mph          # "mph"
```

#### Area
```python
LB.mm2          # "mm²"
LB.kcmil        # "kcmil"
```

#### Force
```python
LB.n            # "N"
LB.lbs          # "lbs"
LB.kn           # "kN"
LB.kip          # "kip"
```

#### Linear Weight
```python
LB.n_per_m      # "N/m"
LB.lb_per_ft    # "lb/ft"
```

#### Pressure & Stress
```python
LB.pa           # "Pa"
LB.lb_per_ft2   # "lbs/ft²"
LB.gpa          # "GPa"
LB.ksi          # "ksi"
```

#### Density
```python
LB.kg_per_m3    # "kg/m³"
LB.lb_per_ft3   # "lb/ft³"
```

#### Electrical
```python
LB.ohm_per_m    # "Ω/m"
LB.ohm_per_mile # "Ω/mile"
LB.kv           # "kV"
LB.a            # "A"
LB.mw           # "MW"
```

#### Dimensionless
```python
LB.ratio        # "–"
LB.degrees      # "°"
LB.dollars      # "$"
LB.count        # "count"
```

### Usage in Results

When returning results, the module includes unit labels:

```python
# Example from get_parameter()
value, unit_label = conductor.get_parameter('area', unit_system='imperial')
# Returns: (987, 'kcmil')

# Display to user
print(f"Conductor area: {value} {unit_label}")
# Output: Conductor area: 987 kcmil
```

## Conversion Factor Naming Convention

All conversion factors follow a consistent naming pattern:

```
CF.{source_unit}_to_{target_unit}
```

Examples:
- `CF.mm2_to_kcmil` - Convert square millimeters to kcmil
- `CF.m_to_ft` - Convert meters to feet
- `CF.c_to_f` - Convert Celsius to Fahrenheit (function)

This makes it easy to discover and use the correct conversion factor.

## Temperature Conversions

Temperature conversions are special because they're non-linear (involve offset):

```python
# Celsius to Fahrenheit
CF.c_to_f(0)    # 32
CF.c_to_f(100)  # 212

# Fahrenheit to Celsius
CF.f_to_c(32)   # 0
CF.f_to_c(212)  # 100
```

Thermal expansion coefficients (per degree) use linear conversions:

```python
# Coefficient per Celsius to per Fahrenheit
coeff_per_f = coeff_per_c * CF.c_to_f_coefficient  # 5/9
```

## Precision Handling

All conversions in `ParameterAccess` apply rounding to avoid floating-point precision issues:

```python
def _convert_value(self, metric_value, param_info, target_unit):
    # ... conversion logic ...
    return math.ceil(round(metric_value * conversion_factor, 10) * 1e6) / 1e6
```

This ensures results are clean and readable while maintaining precision.

## Adding New Conversions

To add a new conversion factor:

1. Add the factor to the `_CF` dataclass in `parameter_access.py`
2. Add the corresponding label to the `_Labels` dataclass
3. Update the `PARAMETER_REGISTRY` if adding a new parameter
4. Update this documentation

Example:
```python
@dataclass(frozen=True)
class _CF:
    # ... existing factors ...
    new_unit_to_old_unit: float = 1.234
    old_unit_to_new_unit: float = 1 / 1.234
```
