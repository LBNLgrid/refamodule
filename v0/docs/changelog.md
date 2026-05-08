# Changelog

## [0.1.0] - 2026-04-30

### Added
- Initial release of REFA (Reconductoring Economic and Financial Analysis Tool)
- IEEE 738 steady-state thermal rating and temperature calculations
- CIGRÉ 324 sag-tension calculations under NESC loading conditions
- Corona inception voltage and voltage gradient assessment (AC and DC)
- Resistive and corona discharge loss calculations (with and without congestion)
- Project types: Rebuild, Reconductoring, VoltageUpgrade, HVDC, Existing, Analysis
- NPV-based economic evaluation over a user-defined time horizon
- 100+ predefined conductors (ACSR, ACSS, ACCC, AECC, ACCR, ACCS)
- NESC 250B loading district profiles (heavy, medium, light, warm islands)
- AC and DC structure configuration support
- Bundled conductor database via `load_bundled_conductors()`
- `str_costs_dol` field on `Conductor` for conductor-specific structure costs
- Full unit test suite (62 tests) covering all calculation methods
- GitHub Actions CI (Python 3.9–3.12) and PyPI publish workflow
