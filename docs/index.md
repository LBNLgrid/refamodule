# REFA

**Reconductoring Economic and Financial Analysis Tool**

The `refa` python module, based on the publicaly-available [REFA tool](https://gridintegration.lbl.gov/refa/), aims to unlock more flexible cases of project cost evaluation and enable advanced extensions by developers.

The REFA tool helps grid planners and policy makers understand the financial and economic costs of different capacity upgrade projects. The tool compares projects under the same economic basis by evaluating the net-present value of costs (NPC), while considering both conventional and advanced conductors.

---

## What REFA Does

Given an existing transmission corridor and a target power capacity requirement, REFA helps grid planners answer:

- Which least-cost conductor can carry the required current without exceeding current or temperature limits?
- What is the sag profile under normal and storm loading conditions?
- Does the operating voltage risk corona discharge?
- What is the net-present cost of each upgrade option over a time horizon (e.g. 40 years)?

REFA evaluates five project types — **Rebuild**, **Reconductoring**, **Voltage Upgrade**, **HVDC conversion**, and **Existing** — and compares them by total cost using the `Analysis` class.

---

## Key Features

| Feature | Details |
|---|---|
| **Techno-economic Analysis** | NPC analysis considering key economic parameters, e.g. cost of capital, inflation, and replacement of structures and conductors |
| **Ampacity** | IEEE 738 steady-state thermal rating |
| **Temperature and Resistance** | IEEE 738 steady-state temperature and resistance at specified current rating |
| **Sag-tension** | CIGRÉ TB-324 sag calculations at peak current and under wind-ice loading profiles |
| **Resistive Line Losses** | Resistive line losses based on calculated condutor resistance and user-specified load factor |
| **Congestion** | Marginal congestion cost modelling |
| **Conductor database** | Example conductors |
| **Corona Discharge** | Inception voltage and voltage gradient clculations |
| **AC and DC** | Separate models for AC and HVDC systems |

---

## Quick Example

```python
from refa import LineDesign, Line, Reconductoring, Analysis
from refa.defaults import (
    default_clear_environment, default_economics,
    acsr_795_0_drake, acss_795_0_cuckoo, accc_1035_dublin,
)

# Describe the line corridor
line_design = LineDesign(
    environment=default_clear_environment(),
    nbr_circuits=1, nbr_bundles=3, nbr_conds_per_bundle=1,
    length_km=30, avg_span_m=300, max_span_m=300,
)

# Build candidate lines
lines = [line_design + acsr_795_0_drake(),
         line_design + acss_795_0_cuckoo(),
         line_design + accc_1035_dublin()]

# Evaluate reconductoring project
project = Reconductoring(
    line_list=lines,
    economics=default_economics(),
    power_mw=400, voltage_kv=230,
    structure_remaining_life=25,
)

print(project.total_costs(time_horizon=40))
```

---

## Standards Implemented

| Standard | Scope |
|---|---|
| **IEEE 738** | Steady-state thermal rating of bare overhead conductors |
| **CIGRÉ 324** | Sag-tension calculation methods for overhead lines |
| **NESC 250B** | Heavy, medium, light, and warm-island loading districts |

---

## License

REFA was developed at Lawrence Berkeley National Laboratory under U.S. Department of Energy funding.
Use of this software is governed by the [Berkeley Lab End User License Agreement](license.md).
