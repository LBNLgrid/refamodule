# REFA

**Reconductoring Economic and Financial Analysis Tool**

REFA is a Python module for techno-economic analysis of transmission line capacity upgrade options. It implements industry-standard electrical and mechanical models to evaluate and compare upgrade strategies — from reconductoring to full HVDC conversion — on a consistent net-present-value basis.

---

## What REFA Does

Given an existing transmission corridor and a target power delivery level, REFA helps engineers answer:

- Which conductor can carry the required current without exceeding thermal or mechanical limits?
- What is the sag profile under normal and storm loading conditions?
- Does the operating voltage risk corona discharge?
- What is the 40-year net present cost of each upgrade option?

REFA evaluates five project types — **Rebuild**, **Reconductoring**, **Voltage Upgrade**, **HVDC conversion**, and **Existing** — and ranks them by total lifecycle cost through the `Analysis` class.

---

## Key Features

| Feature | Details |
|---|---|
| **Ampacity** | IEEE 738 steady-state thermal rating |
| **Sag-tension** | CIGRÉ 324 with NESC 250B loading profiles |
| **Corona** | Inception voltage and voltage gradient (AC and DC) |
| **Losses** | Resistive and corona discharge losses |
| **Congestion** | Marginal congestion cost modelling |
| **Economics** | NPV analysis with WACC, inflation, and replacement scheduling |
| **Conductor database** | 100+ ACSR, ACSS, ACCC, AECC, ACCR, ACCS conductors |
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
