# Changelog

## [0.2.0] - 2026-09-21

### Added
- `StructureConfigLoading` model (`line_angle_deg`, `material_and_geometry`) for mechanical loading calculations, exported from the package top level
- `Line.mechanical_loading()` method computing horizontal structure loading (RUS Bulletin 200) from CIGRÉ 324 sag-tension results
- CIGRÉ 324 sag calculation now also returns intermediate loading parameters (weights and tensions)
- `structure_config_loading` field on all project types (`Existing`, `Rebuild`, `Reconductoring`, `VoltageUpgrade`, `HVDC`)
- Extended default structure configurations and `default_structure_config_loading()` helper
- `rugosity_coefficient` field on `Conductor` (with support for reading it from the conductor CSV), and `extra="allow"` on `ConductorMetric`

### Changed
- Default conductor `solar_absorptivity` changed from 0.5 to 0.6
- Simplified argument validation logic in `system_parameters` (unit normalization and constraint handling)
- Consistent `structure_costs_dol` naming for structure costs across project cost calculations

### Removed
- **Breaking:** `rugosity_coefficient` removed from `Environment` (moved to `Conductor`)
- **Breaking:** `structure_cost_dol` field removed from `LineDesign`

## [0.1.2] - 2026-05-26

### Fixed
- Imperial unit system: loss calculation methods in `line.py` now return metric units when called internally from `project.py` (added `internal_calc` parameter)

### Changed
- Update `docs/index.md` with improved project description linking to the REFA tool

## [0.1.1] - 2026-05-08

### Changed
- Update package author metadata to LBNLgrid

## [0.1.0] - 2026-05-01

### Added
- Initial release of REFA (Reconductoring Economic and Financial Analysis) module
- Unit conversion when accessing different parameters
- Corona inception voltage and voltage gradient assessment
- AC and DC structure configuration support
- NPV-based economic evaluation over user-defined time horizons
- Project types: Rebuild, Reconductoring, VoltageUpgrade, HVDC, Existing, Analysis
- CIGRÉ 324 sag-tension calculations at peak current and under wind-ice loading conditions
- NESC 250B loading district profiles (heavy, medium, light, warm islands)
- Resistive and corona discharge loss calculations (with and without congestion)
- IEEE 738 steady-state thermal rating, temperature, and resistance calculations
- Default conductor database at `src/refa/defaults/conductor.py`
