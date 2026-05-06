# Line Design

`LineDesign` captures the characteristics and circuit configuration of a transmission corridor — excluding the conductor strung on it.

## Fields

| Field | Type | Constraints | Description |
|---|---|---|---|
| `environment` | `Environment` | — | Weather and geographical conditions |
| `nbr_circuits` | `int` | 1–3 | Number of circuits in the line corridor |
| `nbr_bundles` | `int` | 2–3 | Number of phases (AC) or poles (DC) |
| `nbr_conds_per_bundle` | `int` | ≥1 | Conductors per phase or pole |
| `length_km` | `float` | >0 | Total line length (km or mile) |
| `avg_span_m` | `float` | >0 | Average span between structures (m or ft) |
| `max_span_m` | `float` | >0 | Longest individual span (m or ft) |
| `nbr_structures` | `int` | ≥1, optional | Auto-calculated from line length and average span |
| `max_sag_m` | `float` | optional | Maximum allowable sag (m or ft) — required for sag feasibility checks |
| `structure_cost_dol` | `float` | ≥0 | Structure cost specific to used conductor (default `0`) |

## Auto-calculated Fields

If `nbr_structures` is not provided, it is computed automatically:

```
nbr_structures = ceil(length_km × 1000 / avg_span_m) + 1
```

## Construction

```python
from refa import LineDesign
from refa.defaults import default_clear_environment

line_design = LineDesign(
    environment=default_clear_environment(),
    nbr_circuits=1,
    nbr_bundles=3,           # 3-phase AC
    nbr_conds_per_bundle=1,
    length_km=30,
    avg_span_m=300,
    max_span_m=300,
)

print(line_design.nbr_structures)   # 101 (auto-calculated)
```

## Setting a Sag Limit

```python
line_design = LineDesign(
    environment=default_clear_environment(),
    nbr_circuits=1,
    nbr_bundles=3,
    nbr_conds_per_bundle=1,
    length_km=30,
    avg_span_m=300,
    max_span_m=300,
    max_sag_m=10.0,          # sag feasibility will be checked against this
)
```

!!! note "Sag feasibility requires max_sag_m"
    If `max_sag_m` is `None` (the default), `is_sag_feasible()` cannot be evaluated and will be skipped by project feasibility filtering.

## Attribute Proxying

`LineDesign` proxies attribute access to its `Environment`, so you can read environmental properties directly on the design object:

```python
print(line_design.ambient_temperature_c)   # same as line_design.environment.ambient_temperature_c
print(line_design.wind_speed_m_per_s)
```

## Creating a Line with `+`

```python
from refa.defaults import acsr_795_0_drake

line = line_design + acsr_795_0_drake()
# equivalent to: Line(line_design=line_design, conductor=acsr_795_0_drake())
```

## LineDesignImperial

In case of `imperial` unit system, the user can use the same constructor `LineDesign`, which will accept values in imperial units. These are converted to `metric` system with which all internal calculations are conducted.

| metric name —> imperial name |
| `length_km` —> `length_mile` |
| `avg_span_m` —> `avg_span_ft` |
| `max_span_m` —> `max_span_ft` |
| `max_sag_m` —> `max_sag_ft` |
