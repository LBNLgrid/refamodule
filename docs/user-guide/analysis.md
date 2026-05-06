# Analysis

`Analysis` aggregates multiple projects and compares them on any cost metric in a single call.

## Construction

```python
from refa import Analysis

refa = Analysis(project_list=[rebuild, reconductoring, voltageupgrade, hvdc, existing])
```

## Comparison Methods

| Method | Returns |
|---|---|
| `total_costs_of_projects(time_horizon)` | Total capital cost NPV per project |
| `total_costs_of_projects_including_losses(time_horizon, load_factor)` | Capital + losses NPV |
| `conductor_costs_of_projects(time_horizon)` | Conductor cost NPV per project |
| `structure_costs_of_projects(time_horizon)` | Structure cost NPV per project |
| `losses_costs_of_projects(time_horizon, load_factor)` | line losses cost NPV per project (resistive line losses, plus corona losses if applicable) |
| `congestion_costs_of_projects(time_horizon)` | Congestion cost NPV per project|

All methods return a `dict` keyed by project name, with each value being the list of feasible conductor options from that project:

```python
{
    "Rebuild": [
        {"prj_name": "Rebuild", "conductor": "ACSS 795.0_CUCKOO",
         "npv_total_project_costs_mill_dol": 12.16},
        {"prj_name": "Rebuild", "conductor": "ACCC 1035_DUBLIN",
         "npv_total_project_costs_mill_dol": 14.57},
    ],
    "Reconductoring": [
        {"prj_name": "Reconductoring", "conductor": "ACSS 795.0_CUCKOO",
         "npv_total_project_costs_mill_dol": 1.73},
    ],
    "VoltageUpgrade": {},    # empty — all candidates failed feasibility
    "HVDC": {},
    "Existing": [
        {"prj_name": "Existing", "conductor": "ACSS 795.0_CUCKOO",
         "npv_total_project_costs_mill_dol": 1.48},
    ],
}
```

An empty dict `{}` for a project means all candidate conductors failed one or more feasibility checks.

## Example

```python
from refa import Analysis

analysis = Analysis(project_list=[rebuild, recon, vu, hvdc, existing])

# Compare total project costs at a 40-year horizon
results = analysis.total_costs_of_projects(time_horizon=40)

for project_name, options in results.items():
    if not options:
        print(f"{project_name}: no feasible options")
        continue
    for opt in options:
        npv = opt["npv_total_project_costs_mill_dol"]
        cond = opt["conductor"]
        print(f"{project_name} — {cond}: ${npv:.2f}M")
```

## Including Losses

```python
results = analysis.total_costs_of_projects_including_losses(
    time_horizon=40,
    load_factor=0.6,
)
```

## All Years

```python
results = analysis.total_costs_of_projects(time_horizon=40, report_all_years=True)
```

Each option will then contain a column for every year from 0 to `time_horizon - 1` rather than a single final NPV value.
