# refa

Reconductoring Economic and Financial Analysis (REFA) Tool.

The `refa` python module, based on the publicaly-available [REFA tool](https://refa.lbl.gov), aims to unlock more flexible cases of project cost evaluation and enable advanced extensions by developers. 

The REFA tool helps grid planners and policy makers understand the financial and economic costs of different capacity upgrade projects. The tool compares projects under the same economic basis by evaluating the net-present value of costs (NPC), while considering both conventional and advanced conductors.

## Features

- **Techno-economic Analysis** — NPC analysis considering key economic parameters, e.g. cost of capital, inflation, and replacement of structures and conductors 
- **Ampacity** — IEEE 738 steady-state thermal rating 
- **Temperature and Resistance** — IEEE 738 steady-state temperature and resistance at specified current 
- **Sag-tension** — CIGRÉ TB-324 with NESC 250B loading profiles 
- **Resistive Line Losses** — Resistive line losses based on calculated condutor resistance and user-specified load factor
- **Congestion** — Modeling of congestion due to ampacity limits 
- **Conductor database** — Example conductors 
- **Corona Discharge** — Inception voltage and voltage gradient calculations
- **AC and DC** — Separate models for AC and HVDC lines 

## Installation

```bash
pip install refa
```

## Quick Start

```python
from refa import Line, LineDesign, Conductor, Environment
from refa.defaults import default_conductor, default_clear_environment, acsr_795_0_drake
from refa.standards import nesc_250b_heavy

# Build a line
env = default_clear_environment()
conductor = default_conductor()
print(conductor)
line_design = LineDesign(
    nbr_circuits=1,
    nbr_bundles=3,
    nbr_conds_per_bundle=1,
    length_km=25,
    avg_span_m=300,
    max_span_m=350,
    environment=env,
)
line = Line(line_design=line_design, conductor=conductor)

# Check ampacity
print(line.ampacity_at_environment())

# Check feasibility
print(line.is_ampacity_feasible(current_a=1500))
print(line.is_sag_feasible(current_a=1500, max_sag_m=7, loading_conditions=nesc_250b_heavy()))

# Load a typical conductor 
drake = acsr_795_0_drake()
```

## Project Analysis

```python
from refa import Reconductoring, Economics
from refa.defaults import default_economics, acsr_795_0_drake, acsr_556_5_dove

economics = default_economics()

project = Reconductoring(
    conductor_list=[acsr_795_0_drake(), acsr_556_5_dove()],
    line_design=line_design,
    economics=economics,
    power_mw=150,
    voltage_kv=115,
    structure_remaining_life=25
)

results = project.total_costs(time_horizon=65)
```

## Standards Supported

- **IEEE 738** — Standard for calculating the current-temperature relationship of bare overhead conductors
- **CIGRÉ 324** — Sag-tension calculation methods for overhead lines
- **NESC 250B** — National Electrical Safety Code loading districts (heavy, medium, light, warm islands)

## Project Structure

```
refamodule/
├── src/refa/                   # Package source
│   ├── _version.py
│   ├── conductor.py
│   ├── economics.py
│   ├── environment.py
│   ├── line.py
│   ├── line_design.py
│   ├── loading.py
│   ├── project.py
│   ├── structure_config.py
│   ├── data/
│   │   └── conductors.csv      # Bundled conductor database
│   ├── defaults/               # Default configurations
│   └── standards/              # NESC loading profiles
├── examples/
│   └── refa_module_workflow.ipynb
├── tests/
├── pyproject.toml
├── README.md
├── LICENSE
└── CHANGELOG.md
```

## License

See [LICENSE](LICENSE) — REFA is licensed under the Lawrence Berkeley National Laboratory
End User License Agreement (EULA). Use of this software constitutes acceptance of those terms.
