# Installation

## Requirements

- Python 3.9 or later
- pip

## Install from PyPI

```bash
pip install refa
```

## Install from Source

```bash
git clone https://github.com/LBNLgrid/refamodule.git
cd refamodule
pip install -e .
```

## Install with Development Dependencies

```bash
pip install -e ".[dev]"
```

This adds `pytest` and `pytest-cov` for running the test suite.

## Verify Installation

```python
import refa
print(refa.__version__)
```

## Dependencies

| Package | Purpose |
|---|---|
| `numpy` | Numerical calculations (IEEE 738, CIGRÉ 324) |
| `pandas` | Cost calculation DataFrames and NPV output |
| `pydantic` | Input validation and data modelling |
