# Loading

The `Loading` class defines the mechanical loading profile applied to a conductor, including wind pressure, ice thickness, and temperature conditions that affect sag and tension calculations.

## Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `wind_ice_temperature_c` | `float` | — | Temperature at which wind and ice loading occurs (°C, –60° to 60°) |
| `pressure_pa` | `float` | `0` | Wind pressure on conductor (Pa) |
| `ice_thickness_m` | `float` | `0` | Radial ice thickness on conductor (m) |
| `ice_density_kg_per_m3` | `float` | `0` | Density of ice accumulation (kg/m³) |
| `additive_loading_n_per_m` | `float` | `0` | Additional mechanical loading (N/m) |

## Standard Loadings

NESC 250B loading scenarios are provided. 

```python
    from refa.standards import nesc_250b_heavy

    loading = nesc_250b_heavy()
    # wind_ice_temperature_c=-10°C...
```


## Custom Loading

Start from a default and modify

```python
loading = nesc_250b_heavy()
loading.wind_ice_temperature_c=-15.0
loading.pressure_pa=750.0
```

Or construct:

```python
from refa import Loading

loading = Loading(
    wind_ice_temperature_c=-5.0,
    pressure_pa=500.0,
    ice_thickness_m=0.010,
    ice_density_kg_per_m3=900.0,
)
```

!!! tip "Loading combinations"
    The `Loading` class allows independent specification of wind pressure and ice accumulation. In practice, these may occur together (e.g., wind-on-ice scenarios) or separately. Use `pressure_pa` for wind loading and `ice_thickness_m` + `ice_density_kg_per_m3` for ice loading.

## Effect on Calculations

The `Loading` directly affects sag and tension calculations in `Line`. Changing the loading profile will change:

- Conductor sag at the specified temperature
- Tension required to support the combined weight

## LoadingImperial

In case of `imperial` unit system, the user can use the same constructor `Loading`, which will accept values in imperial units. These are converted to `metric` system with which all internal calculations are conducted.

| metric name —> imperial name |
| `wind_ice_temperature_c` —> `wind_ice_temperature_f` |
| `pressure_pa` —> `pressure_lb_per_ft2` |
| `ice_thickness_m` —> `ice_thickness_in` |
| `ice_density_kg_per_m3`  —> `ice_density_lb_per_ft3` | 
| `additive_loading_n_per_m` —> `additive_loading_lbf_per_ft` |
