# Line Calculations

`Line` is the core calculation object. It combines a `LineDesign` and a `Conductor` and exposes all technical analysis methods.

## Construction

```python
from refa import Line, LineDesign
from refa.defaults import default_clear_environment, acss_795_0_cuckoo

ld = LineDesign(
    environment=default_clear_environment(),
    nbr_circuits=1, nbr_bundles=3, nbr_conds_per_bundle=1,
    length_km=10, avg_span_m=250, max_span_m=300,
)

line = Line(line_design=ld, conductor=acss_795_0_cuckoo())
# or: line = ld + acss_795_0_cuckoo()
```

---

## Thermal Calculations (IEEE 738)

REFA implements the IEEE 738 steady-state thermal balance to calculate conductor temperature and ampacity.

### Ampacity

Maximum current the conductor can carry without exceeding its rated temperature at the given environmental conditions.

```python
ampacity = line.ampacity_at_environment()
# 1398 A  (ACSS 795 CUCKOO, clear sky, 25°C, 1 m/s wind, noon, 45°N)
```

### Conductor Temperature

```python
# From current
temp = line.temperature_at_current(current_a=1400)           # 200 °C
temp = line.temperature_at_current(power_mw=550, voltage_kv=345)  # 106 °C
```

### Conductor Resistance

Resistance interpolated between the low and high temperature reference points.

```python
res = line.resistance_at_current(current_a=1400)             # Ω/m
res = line.resistance_at_current(power_mw=550, voltage_kv=345)
```

!!! note "Current vs. power+voltage"
    Most `Line` methods accept **either** `current_a` **or** the pair `(power_mw, voltage_kv)`, but not both. REFA converts power and voltage to current using:

    - AC (3-phase): `I = P / (√3 · V)`
    - DC: `I = P / (2 · V)`

---

## Sag Calculations (CIGRÉ 324)

REFA implements the CIGRÉ 324 catenary sag-tension model. All sag methods require an `initial_tension_percentage` — the initial stringing tension as a fraction of the conductor's rated tensile strength.

### Sag at Steady-State Current

```python
sag = line.sag_at_current(
    current_a=1400,
    initial_tension_percentage=0.2,   # 20% of RTS
)
# 13.6 m
```

### Sag at Power and Voltage

```python
sag = line.sag_at_power_and_voltage(
    power_mw=500, voltage_kv=230,
    initial_tension_percentage=0.2,
)
```

### Sag at a Known Conductor Temperature

```python
sag = line.sag_at_temperature(
    temp_at_current_c=85,
    initial_tension_percentage=0.2,
)
# 10.8 m
```

### Sag Under Mechanical Loading (NESC 250B)

```python
from refa.standards import nesc_250b_heavy

sag = line.sag_at_loading(
    loading_conditions=nesc_250b_heavy(),
    initial_tension_percentage=0.2,
)
# 11.6 m — includes wind pressure and ice load
```

---

## Corona (AC and DC)

Corona calculations require a `StructureConfig` to define phase spacing and structure geometry.

```python
from refa.defaults import default_structure_config_ac, default_structure_config_dc

config_ac = default_structure_config_ac()

# Inception voltage — voltage at which corona begins
v_inc = line.corona_inception_voltage(structure_config=config_ac)   # 230 kV

# Voltage gradient at the conductor surface
v_grad = line.corona_voltage_gradient(structure_config=config_ac)   # 29 kV/cm
```

For DC lines, pass `is_hvdc=True` and a `StructureConfigDC`:

```python
config_dc = default_structure_config_dc()
v_inc_dc = line.corona_inception_voltage(structure_config=config_dc, is_hvdc=True)
```

---

## Losses

### Resistive Losses

Annual energy losses in MWh/m per year, accounting for a load factor.

The loss factor is computed as: `LF = 0.3 × load_factor + 0.7 × load_factor²`

```python
# From current
losses = line.resistive_line_losses(current_a=1400, load_factor=0.6)
# 2.78 MWh/m

# From power — uses congested current when line is congested
losses = line.resistive_line_losses_considering_congestion(
    power_mw=550, voltage_kv=230, load_factor=0.6,
)
# 2.67 MWh/m
```

### Corona Discharge Losses

```python
# AC line
corona_losses = line.corona_discharge_losses(
    voltage_kv=345, load_factor=0.6, structure_config=config_ac,
)
# 0.62 MWh/m

# DC line
corona_losses_dc = line.corona_discharge_losses(
    voltage_kv=345, load_factor=0.6, structure_config=config_dc, is_hvdc=True,
)
# 0.027 MWh/m
```

---

## Congestion

Congestion is the power that would need to be re-routed to alternative paths when the line cannot carry the requested load.

```python
congestion = line.congestion(current_a=1500, voltage_kv=230)  # 1.37 MW
congestion = line.congestion(power_mw=700, voltage_kv=230)    # 14.6 MW
```

A result of `0` means the line can carry the load without congestion.

---

## Overall Technical Performance

Run all calculations in a single call. The returned dictionary grows with each optional parameter provided:

```python
# Minimum — ampacity and sag only
perf = line.overall_technical_performance(current_a=1500)
# {'ampacity_a': 1398.3, 'sag_m': 14.1}

# Add congestion (requires voltage_kv)
perf = line.overall_technical_performance(power_mw=500, voltage_kv=230)
# {'ampacity_a': ..., 'sag_m': ..., 'congestion_mw': 0}

# Add resistive losses (requires load_factor)
perf = line.overall_technical_performance(current_a=1500, load_factor=0.6)
# adds 'resistive_losses_mwh_per_m'

# Add corona (requires structure_config and voltage_kv)
perf = line.overall_technical_performance(
    current_a=1500, voltage_kv=230, load_factor=0.6,
    structure_config=config_ac,
)
# adds 'corona_inception_voltage_kv', 'corona_voltage_gradient_kv_per_cm', 'corona_losses_mwh_per_m'
```
