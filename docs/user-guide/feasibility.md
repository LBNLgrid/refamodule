# Feasibility Checks

Each `Line` exposes three feasibility methods. All return a `(bool, str)` tuple — `True` if the constraint is satisfied, plus a descriptive message when it is not.

---

## Ampacity Feasibility

Checks that:

1. The conductor has **sufficient capacity** — ampacity exceeds the target current.
2. The conductor is **not grossly over-designed** — ampacity is less than 3× the target current.

Both conditions must hold for the check to pass. This dual-bound ensures that candidates that are heavily oversized for the target power level are also excluded.

```python
feasible, msg = line.is_ampacity_feasible(current_a=1300)
# (True, '')

feasible, msg = line.is_ampacity_feasible(current_a=1500)
# (False, 'Ampacity 1398 A is not sufficient for peak current 1500 A.')

# From power and voltage
feasible, msg = line.is_ampacity_feasible(power_mw=200, voltage_kv=115)
# (True, '')  — 200 MW at 115 kV ≈ 1004 A, within [ampacity/3, ampacity]
```

!!! warning "Over-designed lines are also flagged"
    A conductor rated for 1400 A evaluated against a 200 MW / 345 kV target (~335 A) will return `False` because `1400 > 335 × 3 = 1005`. Choose a smaller conductor or a lower voltage for lightly loaded corridors.

---

## Sag Feasibility

Checks that the maximum conductor sag under the given loading does not exceed `max_sag_m`.

```python
feasible, msg = line.is_sag_feasible(
    current_a=1300,
    max_sag_m=10,
    initial_tension_percentage=0.3,
)
```

!!! note "max_sag_m is required"
    `is_sag_feasible` requires an explicit `max_sag_m` argument.
    When sag feasibility is evaluated by a project (`select_sag_feasible=True`), the project uses `line_design.max_sag_m`. If that field is `None`, sag feasibility is skipped.

---

## Corona Feasibility

Checks that the operating voltage does not exceed the corona inception voltage.

```python
feasible, msg = line.is_corona_feasible(
    structure_config=my_config_ac,
    voltage_kv=230,
)
# (True, '')

feasible, msg = line.is_corona_feasible(
    structure_config=my_config_ac,
    voltage_kv=345,
)
# (False, 'Corona inception voltage 230.2 kV is below the line voltage.')
```

---

## Feasibility in Projects

Projects automatically apply all three checks before reporting costs. You can control which checks run:

```python
project.select_ampacity_feasible = True    # default
project.select_sag_feasible = True         # default (requires max_sag_m set on LineDesign)
project.select_corona_feasible = True      # default (requires structure_config on project)
```

Disable a check by setting its flag to `False`:

```python
project.select_sag_feasible = False    # skip sag check for this project
```

Lines that fail any active check are silently excluded from the output. If all candidates fail, the project returns an empty result `{}`.
