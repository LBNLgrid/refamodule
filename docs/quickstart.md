# Quick Start

This page walks through a complete analysis in five steps: build a line, run technical calculations, check feasibility, create projects, and compare them.

## Step 1 — Build a Line

A `Line` combines a `LineDesign` (geometry and circuit configuration) with a `Conductor` (physical and electrical properties).

```python
from refa import LineDesign, Line
from refa.defaults import default_clear_environment, acss_795_0_cuckoo

line_design = LineDesign(
    environment=default_clear_environment(),
    nbr_circuits=1,
    nbr_bundles=3,           # 3-phase AC
    nbr_conds_per_bundle=1,
    length_km=10,
    avg_span_m=250,
    max_span_m=300,
)

line = Line(line_design=line_design, conductor=acss_795_0_cuckoo())

# Shorthand using the + operator
line = line_design + acss_795_0_cuckoo()
```

## Step 2 — Run Technical Calculations

```python
# Thermal
print(line.ampacity_at_environment())                         # 1397 A
print(line.temperature_at_current(current_a=1400))            # 200 °C
print(line.temperature_at_current(power_mw=550, voltage_kv=345))  # 106 °C

# Sag
from refa.standards import nesc_250b_heavy

print(line.sag_at_current(current_a=1400, initial_tension_percentage=0.2))  # 13.6 m
print(line.sag_at_loading(nesc_250b_heavy(), initial_tension_percentage=0.2))  # 11.6 m

# Corona
from refa.defaults import default_structure_config_ac

config_ac = default_structure_config_ac()
print(line.corona_inception_voltage(structure_config=config_ac))   # 230 kV
print(line.corona_voltage_gradient(structure_config=config_ac))    # 29 kV/cm

# Losses
print(line.resistive_line_losses(current_a=1400, load_factor=0.6))  # 2.78 MWh/m
print(line.congestion(current_a=1500, voltage_kv=230))              # 1.4 MW
```

## Step 3 — Check Feasibility

```python
# Ampacity feasibility: checks current < ampacity AND ampacity < 3 × current
feasible, msg = line.is_ampacity_feasible(current_a=1300)
print(feasible)   # True

feasible, msg = line.is_corona_feasible(structure_config=config_ac, voltage_kv=345)
print(feasible)   # False — 345 kV exceeds corona inception voltage of 230 kV
print(msg)

feasible, msg = line.is_sag_feasible(current_a=1300, max_sag_m=10, initial_tension_percentage=0.3)
print(feasible)   # True or False depending on sag result
print(msg)
```

## Step 4 — Create Projects

```python
from refa import Rebuild, Reconductoring, VoltageUpgrade, HVDC, Existing
from refa.defaults import (
    default_economics, default_structure_config_dc,
    acsr_795_0_drake, acss_795_0_cuckoo, accc_1035_dublin,
)

econ = default_economics()

# Rebuild — new conductors + new structures
rebuild = Rebuild(
    conductor_list=[acsr_795_0_drake(), acss_795_0_cuckoo(), accc_1035_dublin()],
    line_design=line_design,
    economics=econ,
    power_mw=400, voltage_kv=230,
    structure_config=default_structure_config_ac(),
)

# Reconductoring — new conductors on existing structures
recon = Reconductoring(
    line_list=[line_design + acss_795_0_cuckoo(), line_design + acsr_795_0_drake()],
    economics=econ,
    power_mw=400, voltage_kv=230,
    structure_remaining_life=25,
)

# VoltageUpgrade — raise operating voltage
vu = VoltageUpgrade(
    line_list=[line_design + acsr_795_0_drake()],
    economics=econ,
    power_mw=400, voltage_kv=345,
    structure_remaining_life=0, conductor_remaining_life=0,
    cost_substations_upgrade_dol=2_000_000,
)

# Existing — baseline with no changes
existing = Existing(
    line_list=[line],
    economics=econ,
    power_mw=400, voltage_kv=230,
    structure_remaining_life=25, conductor_remaining_life=15,
)

print(recon.total_costs(time_horizon=65))
print(rebuild.structure_costs(time_horizon=70))
print(vu.losses_costs(time_horizon=40, load_factor=0.65))

```

## Step 5 — Compare Projects

```python
from refa import Analysis

analysis = Analysis(project_list=[rebuild, recon, vu, existing])
results = analysis.total_costs_of_projects(time_horizon=40)

for project_name, options in results.items():
    print(f"\n{project_name}")
    for opt in options:
        print(f"  {opt['conductor']}: ${opt['npv_total_project_costs_mill_dol']:.2f}M")
```

??? note "Getting all years instead of the final net-present cost"
    Pass `report_all_years=True` to any cost method to receive the cumulative net-present cost at every year up to `time_horizon`:

    ```python
    results = rebuild.total_costs(time_horizon=40, report_all_years=True)
    ```
