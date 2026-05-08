# Projects

All project types inherit from `ProjectEssentials`, which wraps one or more `Line` objects with an `Economics` model and computes net-present-value costs over a specified time horizon.

---

## Common Parameters

All project types share these required fields:

| Field | Type | Description |
|---|---|---|
| `power_mw` | `float` | Target power delivery (MW) |
| `voltage_kv` | `float` | Operating voltage (kV, ≥0) |
| `economics` | `Economics` | Economic and financial assumptions |

And these optional fields:

| Field | Default | Description |
|---|---|---|
| `structure_config` | `None` | Required for corona feasibility |
| `select_ampacity_feasible` | `True` | Filter lines that fail ampacity check |
| `select_sag_feasible` | `True` | Filter lines that fail sag check |
| `select_corona_feasible` | `True` | Filter lines that fail corona check |

## Constructor Patterns

=== "LineDesign + conductor list"
    REFA builds one `Line` per conductor automatically.

    ```python
    project = Rebuild(
        conductor_list=[acsr_795_0_drake(), acss_795_0_cuckoo()],
        line_design=my_line_design,
        economics=my_economics,
        power_mw=400, voltage_kv=230,
    )
    ```

=== "Pre-built line list"
    Pass `Line` objects directly — useful when lines have different designs.

    ```python
    project = Reconductoring(
        line_list=[line1, line2, line3],
        economics=my_economics,
        power_mw=400, voltage_kv=230,
        structure_remaining_life=25,
    )
    ```

---

## Rebuild

Assumes all conductors and structures are replaced at the start of the time horizon. Conductor and structure replacement cycles both start at year 0.

```python
from refa import Rebuild
from refa.defaults import default_structure_config_ac

rebuild = Rebuild(
    conductor_list=[acsr_795_0_drake(), acss_795_0_cuckoo(), accc_1035_dublin()],
    line_design=my_line_design,
    economics=my_economics,
    power_mw=400,
    voltage_kv=230,
    structure_config=default_structure_config_ac(),
)

costs = rebuild.total_costs(time_horizon=65)
# [{'prj_name': 'Rebuild', 'conductor': 'ACSS 795.0_CUCKOO',
#   'npv_total_project_costs_mill_dol': 12.16}, ...]
```

---

## Reconductoring

Conductors are replaced but structures remain. The structure replacement cycle begins after `structure_remaining_life` years.

```python
from refa import Reconductoring

recon = Reconductoring(
    line_list=[my_line_design + acss_795_0_cuckoo(),
               my_line_design + acsr_795_0_drake()],
    economics=my_economics,
    power_mw=400,
    voltage_kv=230,
    structure_remaining_life=25,
)
```

---

## VoltageUpgrade

Raises the operating voltage. Requires an upfront cost for substation and transformer modifications.

```python
from refa import VoltageUpgrade

vu = VoltageUpgrade(
    line_list=[my_line_design + acsr_795_0_drake()],
    economics=my_economics,
    power_mw=400,
    voltage_kv=345,
    structure_remaining_life=0,
    conductor_remaining_life=0,
    cost_substations_upgrade_dol=2_000_000,   # required
)

# Substation cost can be updated after construction
vu.cost_substations_upgrade_dol = 1_500_000

# View substation cost separately
print(vu.substations_upgrade_costs(time_horizon=40))
```

---

## HVDC

Converts the corridor to high-voltage DC. Requires converter station costs. The `nbr_dc_poles_per_circuit` field overwrites `nbr_bundles` on the line to match the DC pole configuration.

```python
from refa import HVDC
from refa.defaults import default_structure_config_dc

hvdc = HVDC(
    line_list=[my_line_design + accc_1035_dublin()],
    economics=my_economics,
    power_mw=400,
    voltage_kv=500,
    structure_remaining_life=0,
    conductor_remaining_life=0,
    cost_converters_dol=3_000_000,   # required
    nbr_dc_poles_per_circuit=2,
    structure_config=default_structure_config_dc(),
)

# Converter cost can be updated after construction
hvdc.cost_converters_dol = 2_500_000

# View converter cost separately
print(hvdc.converter_costs(time_horizon=40))
```

---

## Existing

Models the current line as-is with no changes. Useful as the baseline in an analysis.

```python
from refa import Existing

existing = Existing(
    line_list=[my_line],
    economics=my_economics,
    power_mw=400,
    voltage_kv=230,
    structure_remaining_life=25,    # required
    conductor_remaining_life=15,    # required
)
```

---

## Cost Methods

All project types expose this set of cost methods:

| Method | Returns |
|---|---|
| `total_costs(time_horizon)` | Total capital cost NPV |
| `total_costs_including_losses(time_horizon, load_factor)` | Total cost + losses cost NPV |
| `conductor_costs(time_horizon)` | Conductor-only NPV |
| `structure_costs(time_horizon)` | Structure-only NPV |
| `losses_costs(time_horizon, load_factor)` | Line losses cost NPV |
| `congestion_costs(time_horizon)` | Congestion cost NPV |

All methods return a `list` of `dict`:

```python
[
    {
        "prj_name": "Reconductoring",
        "conductor": "ACSS 795.0_CUCKOO",
        "npv_total_project_costs_mill_dol": 1.73,
    },
    ...
]
```

VoltageUpgrade project has an additional method:

| `substation_upgrade_costs(time_horizon)` | Substation costs |

HVDC project has an additional method:

| `converter_costs(time_horizon)` | Converter costs |

Pass `report_all_years=True` to receive the cumulative NPV at every year up to `time_horizon` rather than just the final value.

---

## Remaining Life

`structure_remaining_life` and `conductor_remaining_life` control when the first replacement investment occurs in the NPV model:

- `0` → the asset is replaced immediately at year 0 (new capital outlay in year 1)
- `25` → the asset continues for 25 years before the first replacement

