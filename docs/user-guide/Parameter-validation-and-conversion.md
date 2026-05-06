# Arguments Validation and Unit Conversion via validate_args Decorator

## Overview

The `validate_args` decorator provides a unified mechanism for:
1. **Validating** function arguments against constraints (e.g., `> 0`, `<= 100`)
2. **Converting** function arguments between metric and imperial units
3. **Adapting** function signatures based on the active unit system

This decorator is applied to methods in `Line` and `ProjectEssentials` classes to ensure robust input handling and seamless unit system support.

## Basic Usage

### Simple Validation

```python
from refa.system_parameters import validate_args, param

@validate_args(
    voltage_kv=param(">", 0, "<", 1000),
    power_mw=param(">", 0, "<", 10000)
)
def get_current(self, power_mw, voltage_kv, is_hvdc=False):
    """Calculate current from power and voltage."""
    return power_mw * 1000 / (voltage_kv * np.sqrt(3))
```

When called:
```python
line.get_current(power_mw=100, voltage_kv=345)  # Valid
line.get_current(power_mw=-50, voltage_kv=345)  # Raises ValueError
```

### Validation with Imperial Conversion

```python
@validate_args(
    max_sag_m=param(
        ">", 0,
        imperial=("max_sag_ft", CF.ft_to_m),
        to_imperial=CF.m_to_ft
    )
)
def is_sag_feasible(self, max_sag_m, ...):
    """Check if sag is feasible."""
    pass
```

When in imperial mode:
```python
UnitSystem.set('imperial')
line.is_sag_feasible(max_sag_ft=10)  # User passes feet
# Decorator converts to meters internally
```

## Constraint Syntax

Constraints are specified as tuples of alternating operators and thresholds:

```python
param(operator1, threshold1, operator2, threshold2, ...)
```

### Supported Operators

| Operator | Meaning |
|----------|---------|
| `">"` | Strictly greater than |
| `">="` | Greater than or equal |
| `"<"` | Strictly less than |
| `"<="` | Less than or equal |
| `"=="` | Equal to |

### Examples

```python
# Single constraint: must be positive
param(">", 0)

# Range constraint: between 0 and 1
param(">=", 0, "<=", 1)

# Multiple constraints: > 0 AND < 1000
param(">", 0, "<", 1000)

# Exact value
param("==", 50)
```

## Imperial Unit Conversion

### Specifying Imperial Parameters

When a parameter has an imperial equivalent, use the `imperial` and `to_imperial` arguments:

```python
@validate_args(
    max_sag_m=param(
        ">", 0,
        imperial=("max_sag_ft", CF.ft_to_m),
        to_imperial=CF.m_to_ft
    )
)
def is_sag_feasible(self, max_sag_m, ...):
    pass
```

**Parameters:**
- `imperial`: Tuple of `(imperial_name, conversion_factor_to_metric)`
  - `imperial_name`: Parameter name users see in imperial mode (e.g., `"max_sag_ft"`)
  - `conversion_factor_to_metric`: Factor to convert imperial to metric (e.g., `CF.ft_to_m`)
- `to_imperial`: Conversion factor from metric to imperial (for display/reverse conversion)

### How It Works

1. **Metric mode** (default):
   - User calls: `is_sag_feasible(max_sag_m=5)`
   - Function receives: `max_sag_m=5` (meters)

2. **Imperial mode**:
   - User calls: `is_sag_feasible(max_sag_ft=16.4)`
   - Decorator converts: `16.4 ft * CF.ft_to_m = 5 m`
   - Function receives: `max_sag_m=5` (meters)
   - Constraints are adjusted: `"> 0"` becomes `"> 0 ft"` (converted to metric)

### Temperature Conversion Example

```python
@validate_args(
    temp_at_current_c=param(
        ">", -60, "<=", 300,
        imperial=("temp_at_current_f", CF.f_to_c),
        to_imperial=CF.c_to_f
    ),
    initial_temperature_c=param(">", 0, "<", 75)
)
def temperature_at_current(self, temp_at_current_c, initial_temperature_c):
    """Calculate temperature at current."""
    pass
```

Usage:
```python
# Metric mode
line.temperature_at_current(temp_at_current_c=50, initial_temperature_c=10)

# Imperial mode
UnitSystem.set('imperial')
line.temperature_at_current(temp_at_current_f=122, initial_temperature_c=50)
# 122°F ≈ 50°C (converted automatically)
```

## Real-World Examples from Line Class

### Example 1: Current Calculation

```python
@validate_args(
    voltage_kv=param(">", 0, "<", 1000),
    power_mw=param(">", 0, "<", 10000)
)
def get_current(self, power_mw, voltage_kv, is_hvdc=False):
    """
    Calculate current from power and voltage.
    
    Args:
        power_mw: Power in MW (must be > 0 and < 10000)
        voltage_kv: Voltage in kV (must be > 0 and < 1000)
        is_hvdc: Whether this is HVDC (default: False)
    
    Returns:
        Current in Amperes
    """
    if is_hvdc:
        return power_mw * 1000 / voltage_kv
    else:
        return power_mw * 1000 / (voltage_kv * np.sqrt(3))
```

### Example 2: Sag Calculation with Temperature

```python
@validate_args(
    temp_at_current_c=param(
        ">", -60, "<=", 300,
        imperial=("temp_at_current_f", CF.f_to_c),
        to_imperial=CF.c_to_f
    ),
    initial_temperature_c=param(">", 0, "<", 75)
)
def sag(self, temp_at_current_c, initial_temperature_c=10, 
         current_a=None, power_mw=None, voltage_kv=None,
         loading_conditions=None, is_hvdc=False):
    """
    Calculate conductor sag using CIGRE 324 method.
    
    Args:
        temp_at_current_c: Temperature at current (°C, range: -60 to 300)
        initial_temperature_c: Initial temperature (°C, range: 0 to 75)
        current_a: Current in Amperes (optional)
        power_mw: Power in MW (optional)
        voltage_kv: Voltage in kV (optional)
        loading_conditions: Loading conditions object (optional)
        is_hvdc: Whether this is HVDC (default: False)
    
    Returns:
        Sag in meters
    """
    # Implementation uses validated and converted parameters
    pass
```

### Example 3: Feasibility Check with Imperial Support

```python
@validate_args(
    current_a=param(">", 0),
    max_sag_m=param(
        ">", 0,
        imperial=("max_sag_ft", CF.ft_to_m),
        to_imperial=CF.m_to_ft
    )
)
def is_sag_feasible(self, current_a, max_sag_m, 
                    initial_tension_percentage=0.35,
                    initial_temperature_c=10,
                    loading_conditions=None, is_hvdc=False):
    """
    Check if sag is feasible for given conditions.
    
    Args:
        current_a: Current in Amperes (must be > 0)
        max_sag_m: Maximum allowable sag in meters (must be > 0)
                   In imperial mode: max_sag_ft (feet)
        initial_tension_percentage: Initial tension as % of RTS (0.1-0.6)
        initial_temperature_c: Initial temperature in °C (0-75)
        loading_conditions: Loading conditions object (optional)
        is_hvdc: Whether this is HVDC (default: False)
    
    Returns:
        Boolean indicating feasibility
    """
    calculated_sag = self.sag(
        temp_at_current_c=...,
        initial_temperature_c=initial_temperature_c,
        current_a=current_a,
        loading_conditions=loading_conditions,
        is_hvdc=is_hvdc
    )
    return calculated_sag <= max_sag_m
```

## Real-World Examples from ProjectEssentials Class

### Example 1: Cost Calculation

```python
@validate_args(
    time_horizon=param(">", 0, "<=", 100)
)
def total_costs(self, time_horizon, report_all_years=False):
    """
    Calculate total project costs over time horizon.
    
    Args:
        time_horizon: Analysis period in years (must be > 0 and <= 100)
        report_all_years: Whether to report costs for each year (default: False)
    
    Returns:
        Dictionary of costs or DataFrame if report_all_years=True
    """
    # Implementation uses validated time_horizon
    pass
```

### Example 2: Multi-Parameter Validation

```python
@validate_args(
    time_horizon=param(">", 0, "<=", 100),
    load_factor=param(">=", 0, "<=", 1)
)
def total_costs_including_losses(self, time_horizon, load_factor, 
                                 report_all_years=False):
    """
    Calculate total costs including loss costs.
    
    Args:
        time_horizon: Analysis period in years (0 < time_horizon <= 100)
        load_factor: Load factor as fraction (0 <= load_factor <= 1)
        report_all_years: Whether to report costs for each year (default: False)
    
    Returns:
        Dictionary of costs or DataFrame if report_all_years=True
    """
    # Implementation uses both validated parameters
    pass
```

## Error Handling

### Validation Errors

When a constraint is violated, a `ValueError` is raised:

```python
try:
    line.get_current(power_mw=-50, voltage_kv=345)
except ValueError as e:
    print(e)
    # Output: 'power_mw' = -50 is out of range: must be > 0
```

### Configuration Errors

If the decorator is misconfigured, errors are raised at decoration time:

```python
# Error: parameter name not in function signature
@validate_args(unknown_param=param(">", 0))
def my_function(self, known_param):
    pass
# Raises: ValueError: validate() key 'unknown_param' not found in my_function signature
```

## Signature Adaptation

The decorator automatically adapts the function signature based on the active unit system:

```python
@validate_args(
    max_sag_m=param(
        ">", 0,
        imperial=("max_sag_ft", CF.ft_to_m),
        to_imperial=CF.m_to_ft
    )
)
def is_sag_feasible(self, max_sag_m, ...):
    pass

# In metric mode
help(line.is_sag_feasible)
# Shows: is_sag_feasible(self, max_sag_m, ...)

UnitSystem.set('imperial')

# In imperial mode
help(line.is_sag_feasible)
# Shows: is_sag_feasible(self, max_sag_ft, ...)
```

## Best Practices

### 1. Always Validate User Input

```python
# Good: Validates all user-facing parameters
@validate_args(
    voltage_kv=param(">", 0, "<", 1000),
    power_mw=param(">", 0, "<", 10000)
)
def get_current(self, power_mw, voltage_kv):
    pass

# Avoid: No validation
def get_current(self, power_mw, voltage_kv):
    pass
```

### 2. Use Realistic Constraints

```python
# Good: Realistic physical constraints
@validate_args(
    voltage_kv=param(">", 0, "<", 1000),  # Typical transmission voltages
    power_mw=param(">", 0, "<", 10000)    # Typical transmission power
)

# Avoid: Unrealistic constraints
@validate_args(
    voltage_kv=param(">", 0, "<", 1e10),  # Unrealistic upper bound
    power_mw=param(">", 0, "<", 1e20)     # Unrealistic upper bound
)
```

### 3. Handle None Values

The decorator automatically skips validation for `None` values:

```python
@validate_args(current_a=param(">", 0))
def my_function(self, current_a=None):
    if current_a is None:
        # Handle None case
        pass
    else:
        # current_a is guaranteed to be > 0
        pass
```

## Implementation Details

### Constraint Checking

Constraints are checked using Python's comparison operators:

```python
OPERATORS = {
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
}
```

### Unit System Detection

The decorator detects the active unit system at decoration time:

```python
def validate_args(**param_rules):
    imperial = UnitSystem.is_imperial()
    
    if imperial:
        # Use imperial parameter names and constraints
    else:
        # Use metric parameter names and constraints
```

### Conversion Application

When in imperial mode, the decorator:
1. Accepts imperial parameter names
2. Validates against converted constraints
3. Converts values to metric
4. Passes metric values to the function

```python
# User calls (imperial mode)
is_sag_feasible(max_sag_ft=16.4)

# Decorator converts
max_sag_m = 16.4 * CF.ft_to_m  # 5 meters

# Decorator validates
assert max_sag_m > 0  # ✓ Passes

# Function receives
is_sag_feasible(max_sag_m=5)
```
