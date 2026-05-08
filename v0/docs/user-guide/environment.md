# Environment

The `Environment` class captures weather and geographic conditions that affect conductor heat balance, sag, and corona calculations.

## Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `date` | `date` | today | Reference date (affects solar angle and heat gain) |
| `latitude` | `float` | — | Geographic latitude in degrees (–90° to 90°) |
| `elevation_m` | `float` | — | Site elevation above sea level (m) |
| `wind_speed_m_per_s` | `float` | — | Wind speed (m/s) |
| `wind_angle` | `int` | — | Angle between wind and conductor axis (0–90°) |
| `cw_angle_direction_rel_to_north` | `int` | — | Conductor orientation relative to north (0–90°) |
| `hour` | `int` | — | Hour of day for solar calculations (0–24) |
| `atmosphere` | `dict` | — | Polynomial coefficients (A–G) for solar heat flux |
| `ambient_temperature_c` | `float` | — | Ambient air temperature (°C) |
| `weather_correction_factor` | `float` | `1.0` | Set to `0.8` for rainy conditions |
| `rugosity_coefficient` | `float` | `0.82` | Conductor surface roughness: `1.0` polished, `0.92–0.98` dirty, `0.80–0.87` stranded |

## Default Environments

Two pre-configured environments are provided.

=== "Clear sky"
    ```python
    from refa.defaults import default_clear_environment

    env = default_clear_environment()
    # latitude=45°N, elevation=100 m, wind=1 m/s, ambient=25°C, hour=12
    ```

=== "Industrial atmosphere"
    ```python
    from refa.defaults import default_industrial_environment

    env = default_industrial_environment()
    # Same geometry, but with industrial pollution atmosphere coefficients
    ```

## Custom Environment

```python
import datetime
from refa import Environment
from refa.defaults import default_clear_environment

# Start from the default and modify
env = default_clear_environment()
env.date = datetime.date(2025, 7, 15)
env.ambient_temperature_c = 35.0
env.wind_speed_m_per_s = 0.6       # Low wind — conservative rating
env.weather_correction_factor = 0.8  # Rainy conditions
```

Or construct from scratch:

```python
env = Environment(
    date=datetime.date(2025, 7, 15),
    latitude=34.0,
    elevation_m=200.0,
    wind_speed_m_per_s=0.6,
    wind_angle=45,
    cw_angle_direction_rel_to_north=0,
    hour=14,
    atmosphere={"A": -42.2391, "B": 63.8044, "C": -1.922,
                "D": 0.0346921, "E": -0.000361118,
                "F": 1.94318e-06, "G": -4.07608e-09},
    ambient_temperature_c=35.0,
)
```

!!! tip "Atmosphere coefficients"
    The `atmosphere` dict contains the A–G polynomial coefficients for the Leckner solar heat flux model used in IEEE 738. Use `default_clear_environment()` or `default_industrial_environment()` as starting points, or consult the IEEE 738 standard for site-specific values.

## Effect on Calculations

The `Environment` directly drives the IEEE 738 thermal balance equation inside `Line`. Changing the date, hour, latitude, or wind speed will change:

- Ampacity (`ampacity_at_environment()`)
- Steady-state conductor temperature
- All sag calculations that depend on computed conductor temperature
- Losses calculations that depend on computed conductor resistance
- Congestion (which depends on available ampacity)


## EnvironmentImperial

In case of `imperial` unit system, the user can use the same constructor `Environment`, which will accept values in imperial units. These are converted to `metric` system with which all internal calculations are conducted.

| metric name —> imperial name |
| `elevation_m`  —> `elevation_ft`|
| `wind_speed_m_per_s`  —> `wind_speed_mph`|
| `ambient_temperature_c` —> `ambient_temperature_f`|
