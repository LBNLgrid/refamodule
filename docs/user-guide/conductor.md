# Conductor

The `Conductor` class holds all physical, electrical, and cost properties of a bare overhead conductor.

## Fields

### Physical

| Field | Unit | Description |
|---|---|---|
| `type` | — | Conductor family: `ACSR`, `ACSS`, `ACCC`, `AECC`, `ACCR`, `ACCS` |
| `code` | — | Identifier (e.g., `795.0_DRAKE`) |
| `area_mm2` | mm² | Cross-sectional area |
| `diameter_mm` | mm | Outer diameter |
| `weight_n_per_m` | N/m | Linear weight |
| `conductor_rts_kn` | kN | Rated tensile strength |
| `elastic_modulus_gpa` | GPa | Young's modulus (for sag-tension) |
| `coeff_thermal_expan_per_cel` | 1/°C | Coefficient of thermal expansion |

### Electrical

| Field | Unit | Description |
|---|---|---|
| `temp_dc_c` | °C | Reference temperature for DC resistance |
| `temp_low_c` | °C | Low reference temperature (typically 25°C) |
| `temp_high_c` | °C | High reference temperature (typically 75°C) |
| `max_temperature_c` | °C | Maximum continuous operating temperature |
| `res_dc_ohm_per_m` | Ω/m | DC resistance at `temp_dc_c` |
| `res_low_ohm_per_m` | Ω/m | AC resistance at `temp_low_c` |
| `res_high_ohm_per_m` | Ω/m | AC resistance at `temp_high_c` |
| `emissivity` | — | Thermal emissivity (0–1) |
| `solar_absorptivity` | — | Solar absorptivity (0–1) |

### Cost

| Field | Unit | Description |
|---|---|---|
| `dol_per_1000_ft` | $/1000 ft | Conductor material cost |
| `inst_dol_per_1000_ft` | $/1000 ft | Installation labour cost |
| `accessories_dol_per_1000_ft` | $/1000 ft | Hardware and accessories cost |
| `str_costs_dol` | $ | Conductor-specific structure cost (default `0.0`) |

## Using the Bundled Database

The package ships with over 100 conductors in `src/refa/data/conductors.csv`. Load them all at once:

```python
from refa.defaults import load_bundled_conductors

conductors = load_bundled_conductors()

# Dot-notation access — each entry is a zero-argument factory function
drake   = conductors.acsr_795_0_drake()
cuckoo  = conductors.acss_795_0_cuckoo()
pelican = conductors.acsr_477_0_pelican()
```

Key names follow the pattern `{type}_{kcmil}_{name}` in lowercase with dots and spaces replaced by underscores.

### Individual factory functions

Frequently used conductors are also importable directly:

```python
from refa.defaults import (
    acsr_795_0_drake,
    acss_795_0_cuckoo,
    accc_1035_dublin,
    default_conductor,   # ACSR 556.5 DOVE
)

drake = acsr_795_0_drake()
```

## Loading from a Custom CSV

Bring your own conductor data in the same column format as the bundled CSV:

```python
from refa.defaults import load_conductors_from_csv

my_conductors = load_conductors_from_csv("path/to/my_conductors.csv")
custom = my_conductors.acsr_500_0_hawk()
```

**Required CSV columns:**

`code`, `type`, `dol_per_1000_ft`, `inst_dol_per_1000_ft`, `accessories_dol_per_1000_ft`,
`str_costs_dol`, `area_mm2`, `diameter_mm`, `weight_n_per_m`, `conductor_rts_kn`,
`temp_low_c`, `temp_high_c`, `max_temperature_c`, `res_low_ohm_per_m`, `res_high_ohm_per_m`,
`elastic_modulus_gpa`, `coeff_thermal_expan_per_cel`, `temp_dc_c`, `res_dc_ohm_per_m`,
`emissivity`, `solar_absorptivity`

## Manual Construction

```python
from refa import Conductor

c = Conductor(
    type="ACSR",
    code="266.8_PARTRIDGE",
    area_mm2=157.0,
    diameter_mm=16.0,
    weight_n_per_m=5.36,
    conductor_rts_kn=50.26,
    dol_per_1000_ft=735.0,
    inst_dol_per_1000_ft=1027.0,
    accessories_dol_per_1000_ft=263.0,
    temp_dc_c=20.0,
    temp_low_c=25.0,
    temp_high_c=75.0,
    max_temperature_c=100.0,
    res_dc_ohm_per_m=0.000209,
    res_low_ohm_per_m=0.000209,
    res_high_ohm_per_m=0.000256,
    elastic_modulus_gpa=75.5,
    coeff_thermal_expan_per_cel=1.92e-05,
    emissivity=0.5,
    solar_absorptivity=0.5,
)
```

## Conductor Types

| Type | Core material | Max temp | Notes |
|---|---|---|---|
| ACSR | Steel | 100°C | Standard aluminium conductor steel reinforced |
| ACSS | Steel (annealed) | 200°C | High-temperature, self-damping |
| ACCC | Carbon composite | 180–200°C | Lightweight, low sag |
| AECC | Carbon composite | — | Extended capacity composite core |
| ACCR | Aluminium matrix composite | 210°C | High-strength composite core |
| ACCS | Steel | — | Compact stranding variant |
