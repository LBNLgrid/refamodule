# refa

Transmission line analysis and optimization module for AC/DC power systems.

`refa` implements IEEE 738 (steady-state thermal rating) and CIGRÉ 324 (sag-tension) standards to evaluate and compare line upgrade projects including reconductoring, voltage upgrades, and HVDC conversion.

## Features

- **Ampacity** — IEEE 738 steady-state current rating and temperature calculations
- **Sag-tension** — CIGRÉ 324 sag calculations under NESC loading conditions
- **Corona** — inception voltage and voltage gradient assessment
- **Losses** — resistive and corona discharge losses with and without congestion
- **Project types** — Rebuild, Reconductoring, VoltageUpgrade, HVDC, Existing, Analysis
- **Economics** — NPV-based cost comparison over a user-defined time horizon
- **Conductor database** — 100+ predefined ACSR, ACSS, ACCC, AECC, ACCR, ACCS conductors
- **AC/DC support** — separate structure configs and calculations for AC and DC systems

## Installation

```bash
pip install refa
```

## Quick Start

```python
from refa import Line, LineDesign, Conductor, Environment
from refa.defaults import default_conductor, default_clear_environment, load_bundled_conductors
from refa.standards import nesc_250b_heavy

# Build a line
env = default_clear_environment()
conductor = default_conductor()
line_design = LineDesign(
    circuits=1,
    bundles=1,
    conductors_per_bundle=1,
    span_m=300,
    environment=env,
)
line = Line(line_design=line_design, conductor=conductor)

# Check ampacity
print(line.ampacity(max_conductor_temp_c=75))

# Check feasibility
print(line.is_ampacity_feasible(current_a=500))
print(line.is_sag_feasible(loading=nesc_250b_heavy()))

# Load all bundled conductors
conductors = load_bundled_conductors()
drake = conductors.acsr_795_0_drake()
```

## Project Analysis

```python
from refa import Reconductoring, Economics
from refa.defaults import default_economics, load_bundled_conductors

conductors = load_bundled_conductors()
economics = default_economics()

project = Reconductoring(
    conductor_list=[conductors.acsr_795_0_drake(), conductors.acsr_556_5_dove()],
    line_design=line_design,
    economics=economics,
    time_horizon=40,
    peak_power_mw=200,
    voltage_kv=115,
)

results = project.overall_technical_performance()
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
