# Defaults API Reference

## Conductor Defaults

::: refa.defaults.conductor.default_conductor

::: refa.defaults.conductor.default_conductor_imperial

::: refa.defaults.conductor.load_conductors_from_csv

### Named Conductors

Individual conductor factory functions follow the naming pattern
`{type}_{kcmil}_{name}()`, e.g. `acsr_795_0_drake()`, `acss_795_0_cuckoo()`.
They are importable directly from `refa.defaults`:

```python
from refa.defaults import acsr_795_0_drake, acss_795_0_cuckoo, accc_1035_dublin
```

::: refa.defaults.conductor.acsr_795_0_drake

::: refa.defaults.conductor.acss_795_0_cuckoo

::: refa.defaults.conductor.accc_1035_dublin

## Environment Defaults

::: refa.defaults.environment.default_clear_environment

::: refa.defaults.environment.default_industrial_environment

::: refa.defaults.environment.default_clear_environment_imperial

::: refa.defaults.environment.default_industrial_environment_imperial

## Economics Defaults

::: refa.defaults.economics.default_economics

## Structure Config Defaults

::: refa.defaults.structure_config.default_structure_config_ac

::: refa.defaults.structure_config.default_structure_config_dc

::: refa.defaults.structure_config.default_structure_config_ac_imperial

::: refa.defaults.structure_config.default_structure_config_dc_imperial
