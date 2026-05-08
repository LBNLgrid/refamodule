# ParameterAccess: Setter/Getter Functions

## Overview

The `ParameterAccess` class provides a unified interface for getting and setting parameters across the REFA module objects, including automatic unit conversion. It enables seamless interaction with parameters in both metric and imperial unit systems without requiring manual conversion.

## Core Exposed Functions

### `get_parameter(parameter_name, unit_system=None)`

Retrieves a parameter value in with the current unit, or optionally in the specified `unit_system`.

**Parameters:**
- `parameter_name` (str): Name of the parameter to retrieve (e.g., `'area'`, `'diameter'`, `'elevation'`)
- `unit_system` (str, optional): Target unit system - `'metric'`, `'imperial'`, or `None` (uses current system from config)

**Returns:**
- Tuple of `(value, unit_label)` where:
  - `value`: The parameter value in the requested unit system
  - `unit_label`: String representation of the unit (e.g., `'mm²'`, `'kcmil'`)

**Example:**
```python
from refa.conductor import ConductorMetric
from refa.system_parameters import UnitSystem

# Create a conductor with metric values
conductor = ConductorMetric(
    area_mm2=500,
    diameter_mm=25.4,
    # ... other parameters
)

# Get area in metric (current system)
area_metric, unit_metric = conductor.get_parameter('area')
# Returns: (500, 'mm²')

# Get area in imperial
area_imperial, unit_imperial = conductor.get_parameter('area', unit_system='imperial')
# Returns: (987, 'kcmil')  # approximately
```

### `set_parameter(parameter_name, value, unit_system=None)`

Sets a parameter value with automatic conversion to internal metric storage. The parameter `unit_system` is used to specify that this entry is provided in a different system than the current global unit system.

**Parameters:**
- `parameter_name` (str): Name of the parameter to set
- `value` (float): The value to set
- `unit_system` (str, optional): Unit system of the input value - `'metric'`, `'imperial'`, or `None` (uses current system)

**Example:**
```python
# Set area in metric
conductor.set_parameter('area', 500, unit_system='metric')

# Set area in imperial (automatically converts to metric for storage)
conductor.set_parameter('area', 987, unit_system='imperial')
# Internally stored as ~500 mm²

# Set using current unit system from config
conductor.set_parameter('diameter', 25.4)
```

### `get_parameter_info(parameter_name)`

Retrieves metadata about a parameter including its internal name and unit definitions.

**Parameters:**
- `parameter_name` (str): Name of the parameter

**Returns:**
- Dictionary with keys:
  - `'internal_name'`: The actual field name in the model (e.g., `'area_mm2'`)
  - `'metric_unit'`: Metric unit abbreviation (e.g., `'mm2'`)
  - `'imperial_unit'`: Imperial unit abbreviation (e.g., `'kcmil'`)
  - `'description'`: Human-readable description

**Example:**
```python
info = conductor.get_parameter_info('area')
# Returns: {
#     'internal_name': 'area_mm2',
#     'metric_unit': 'mm2',
#     'imperial_unit': 'kcmil',
#     'description': 'Conductor cross-sectional area'
# }
```

### `list_parameters()`

Returns a list of all available parameters for the model, including:
- Parameters with unit conversion (from `_parameter_map`)
- Dimensionless fields (no conversion needed)
- Parameters from nested objects (if applicable)

**Returns:**
- List of parameter names (strings)

**Example:**
```python
params = conductor.list_parameters()
# Returns: ['area', 'diameter', 'weight', 'conductor_rts', 'temp_dc', ...]
```

### `get_all_parameters(unit_system=None)`

Retrieves all parameters (with their values and units) as a dictionary in the specified unit system.

**Parameters:**
- `unit_system` (str, optional): Target unit system - `'metric'`, `'imperial'`, or `None`

**Returns:**
- Dictionary mapping parameter names to `(value, unit_label)` tuples

**Example:**
```python
all_params = conductor.get_all_parameters(unit_system='imperial')
# Returns: {
#     'area': (987, 'kcmil'),
#     'diameter': (1.0, 'in'),
#     'weight': (0.15, 'lbs/kft'),
#     ...
# }
```

### `get_parameter_registry_for_class()` (Class Method)

Returns the parameter registry entry for the model class.

**Returns:**
- Dictionary mapping parameter names to their metadata

**Example:**
```python
registry = Line.get_parameter_registry_for_class()
# Returns the full parameter map for Line
```

### `get_parameters_needing_conversion()` (Class Method)

Returns a list of all parameters that require unit conversion for this model.

**Returns:**
- List of parameter names that have metric/imperial conversions

**Example:**
```python
convertible = ConductorMetric.get_parameters_needing_conversion()
# Returns: ['area', 'diameter', 'weight', 'conductor_rts', ...]
```

## Supported Models

The `ParameterAccess` interface is available on:

- **`ConductorMetric`**: Conductor properties (area, diameter, weight, resistance, etc.)
- **`EnvironmentMetric`**: Environmental conditions (elevation, wind speed, temperature)
- **`LineDesignMetric`**: Line geometry (length, span, sag)
- **`LoadingMetric`**: Loading conditions (ice, wind, pressure)
- **`StructureConfigACmetric`**: AC structure geometry
- **`StructureConfigDCmetric`**: DC structure geometry
- **`Line`**: Composite model with nested conductor and line_design
- **`ProjectEssentials`**: Project with nested economics and line_design (and all classes inheriting from ProjectEssentials: Rebuild, Reconductoring, VoltageUpgrade, HVDC, and Existing)

## Unit System Configuration

The default unit system is read from `refa/system_parameters/config.toml`:

```toml
[units]
unit_system = "metric"  # or "imperial"
```

It is recommended to chang the unit system before importing from the REFA module. To check the active unit system at runtime:

```python
from refa.system_parameters import UnitSystem

UnitSystem.is_metric()  # True if metric, False otherwise
UnitSystem.is_imperial()  # True if imperial, False otherwise
```

## Internal Architecture

### Parameter Registry

All parameters are defined in a centralized `PARAMETER_REGISTRY` dictionary that maps:
- Model class name → Parameter name → Metadata (internal field name, metric unit, imperial unit, description)

This ensures a single source of truth for all unit conversions.

### Conversion Factors (CF)

The `CF` object provides all conversion factors:

```python
from refa.system_parameters import CF

CF.mm2_to_kcmil      # 1.974
CF.kcmil_to_mm2      # 0.5067
CF.m_to_ft           # 3.28084
CF.ft_to_m           # 0.3048
CF.c_to_f(celsius)   # Temperature conversion function
CF.f_to_c(fahrenheit) # Temperature conversion function
```

### Unit Labels (LB)

The `LB` object provides display labels for all units:

```python
from refa.system_parameters import LB

LB.mm2      # "mm²"
LB.kcmil    # "kcmil"
LB.m        # "m"
LB.ft       # "ft"
LB.celsius  # "°C"
LB.fahrenheit # "°F"
```

## Nested Parameter Access

For composite models like `Line` and `ProjectEssentials`, parameters from nested objects are accessible as follows:

```python
from refa.line import Line
from refa.conductor import ConductorMetric
from refa.line_design import LineDesignMetric

line = Line(
    conductor=ConductorMetric(...),
    line_design=LineDesignMetric(...)
)

# Access conductor parameter directly from line
area, unit = line.conductor.get_parameter('area')  

# Access line_design parameter directly from line
length, unit = line.line_design.get_parameter('length')  
```

## Error Handling

All functions raise `ValueError` if:
- An unknown parameter name is provided
- An invalid unit system is specified (not 'metric' or 'imperial')
- A parameter is not found in the model

Example:
```python
try:
    conductor.get_parameter('unknown_param')
except ValueError as e:
    print(f"Error: {e}")
    # Error: Unknown parameter 'unknown_param'. Available: ['area', 'diameter', ...]
```
