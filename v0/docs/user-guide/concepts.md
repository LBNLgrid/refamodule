# Overview

## The REFA Workflow

REFA is structured around a hierarchy of objects. Each layer adds more context until a full project analysis is possible.

```
Environment         OptionalObjects(Loading, StructureConfig)
    │                   |           |
    ▼                   ▼           |
LineDesign ─────────────┐           |                       
                        ▼           ▼                        
                       Line  ──► Project (Rebuild /       ────────► Analysis
                        ▲           ▲     Reconductoring /
Conductor ──────────────┘           |     VoltageUpgrade /
                                    |     HVDC / Existing)
Economics ──────────────────────────┘     
```

### Layer 1 — Input Objects 

`Environment` is an independent object holding attributes needed for all technical calculations. Some other necessary technical attributes are provided through objects (`Loading`, `StructureConfig`) or directly as attributes of hierarchically higher objects.
Economic attributes are provided in `Economics` to feed any type of project creation.

### Layer 2 — LineDesign & Conductor

`LineDesign` appends an `Environment` to its other attributes defining the configuration of the corridor (length, spans, circuits, bundles). The `LineDesign` is independent of which `Conductor` will be strung.

### Layer 3 — Line

`Line` pairs a `LineDesign` with a `Conductor`. All technical calculations (ampacity, sag, corona, losses, congestion) live here. You can build a `Line` with the constructor or with the `+` shorthand:

```python
line = Line(line_design=ld, conductor=c)
line = ld + c          # same result
line = c + ld          # same result
```

### Layer 4 — Project

A project wraps one or more `Line` objects and an `Economics` object to produce net-present-value of cost estimates. Five project types are available:

| Class | Description |
|---|---|
| `Rebuild` | New conductors and new structures from the start |
| `Reconductoring` | New conductors on existing structures |
| `VoltageUpgrade` | Raise operating voltage; replace conductors and possibly structures |
| `HVDC` | HVDC line; replace conductors and possibly structures |
| `Existing` | Baseline — current line, no changes |

Projects can be constructed in two ways:

=== "From a single line design and a conductor list"
    ```python
    project = Rebuild(
        conductor_list=[drake(), cuckoo(), dublin()],
        line_design=ld,
        economics=econ,
        power_mw=400, voltage_kv=230,
    )
    ```

=== "From a list of lines"
    ```python
    project = Reconductoring(
        line_list=[ld + drake(), ld + cuckoo()],
        economics=econ,
        power_mw=400, voltage_kv=230,
        structure_remaining_life=25,
    )
    ```

### Layer 5 — Analysis

`Analysis` takes a list of projects and produces a side-by-side comparison for any cost metric.

```python
refa = Analysis(project_list=[rebuild, recon, vu, hvdc, existing])
refa.total_costs_of_projects(time_horizon=40)
```

---

## Feasibility Filtering

Before reporting costs, every project automatically filters out lines that fail technical constraints:

- **Ampacity** (`select_ampacity_feasible=True`) — the conductor must carry the target current without exceeding its rated temperature, and the ampacity must not exceed 3× the target current (over-designed lines are excluded).
- **Sag** (`select_sag_feasible=True`) — the maximum sag must not exceed `line_design.max_sag_m` if set.
- **Corona** (`select_corona_feasible=True`) — the operating voltage must not exceed the corona inception voltage.

Any of these filters can be disabled:

```python
project.select_ampacity_feasible = False
project.select_corona_feasible = False
```

---

## AC vs. DC

Pass `is_hvdc=True` to any `Line` method to use DC-specific equations. The `HVDC` project sets this automatically for all its internal calculations.
