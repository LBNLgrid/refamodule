# Changelog

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
