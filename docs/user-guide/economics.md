# Economics

The `Economics` class holds all financial assumptions used in NPV calculations.

## Fields

| Field | Default | Description |
|---|---|---|
| `conductors_lifetime` | 40 years | Years between conductor replacements |
| `structures_lifetime` | 60 years | Years between structure replacements |
| `wacc` | 0.07 | Weighted average cost of capital (7%) |
| `inflation` | 0.02 | Annual inflation rate (2%) |
| `cost_of_losses_dol_per_mwh` | $40/MWh | Value of energy lost to resistive and corona losses |
| `cost_of_congestion_dol_per_mwh` | $1/MWh | Value of energy re-routed due to congestion |
| `cost_of_structures_dol_per_unit` | $100,000 | Per-structure cost when `structure_costs_specific_to_conductor=False` |
| `tgt_structure_cost_dol` | — | Tangent structure unit cost |
| `ra_structure_cost_dol` | — | Running angle structure unit cost |
| `nade_structure_cost_dol` | — | Non-angled deadend structure unit cost |
| `de_structure_cost_dol` | — | Deadend structure unit cost |

## Default Economics

```python
from refa.defaults import default_economics

econ = default_economics()
# conductors_lifetime=40, structures_lifetime=60
# wacc=7%, inflation=2%
# losses=$40/MWh, congestion=$1/MWh, structures=$100k/unit
```

## Custom Economics

```python
from refa import Economics

econ = Economics(
    conductors_lifetime=35,
    structures_lifetime=50,
    wacc=0.09,
    inflation=0.03,
    cost_of_losses_dol_per_mwh=55.0,
    cost_of_congestion_dol_per_mwh=5.0,
    cost_of_structures_dol_per_unit=120_000,
    tgt_structure_cost_dol=80_000,
    ra_structure_cost_dol=100_000,
    nade_structure_cost_dol=130_000,
    de_structure_cost_dol=150_000,
)
```

## NPV Methodology

For each year `t` in the time horizon, costs are discounted and inflated as:

```
NPV contribution at year t = cost × (1 + inflation)^t / (1 + WACC)^t
```

Capital costs (conductor and structure) are only incurred in years when a replacement is scheduled:

- First conductor replacement: at `conductor_remaining_life`, then every `conductors_lifetime` years.
- First structure replacement: at `structure_remaining_life`, then every `structures_lifetime` years.

Operating costs (losses, congestion) are incurred every year.

All reported NPV values are in **millions of dollars** (`mill_dol`).
