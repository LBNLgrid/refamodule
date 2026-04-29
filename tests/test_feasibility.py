"""Tests for Line feasibility checks."""
import pytest


def test_corona_feasible_below_threshold(line1, structure_config_ac):
    """Voltage below corona inception voltage — should be feasible."""
    feasible, _ = line1.is_corona_feasible(
        structure_config=structure_config_ac, voltage_kv=200
    )
    assert feasible is True


def test_corona_not_feasible_above_threshold(line1, structure_config_ac):
    """345 kV exceeds corona inception voltage of ~230 kV — should not be feasible."""
    feasible, message = line1.is_corona_feasible(
        structure_config=structure_config_ac, voltage_kv=345
    )
    assert feasible is False
    assert "230" in message


def test_ampacity_feasible_below_limit(line1):
    """Current well below ampacity (~1398 A) — should be feasible."""
    feasible, _ = line1.is_ampacity_feasible(current_a=1000)
    assert feasible is True


def test_ampacity_not_feasible_above_limit(line1):
    """Current above ampacity — should not be feasible."""
    feasible, _ = line1.is_ampacity_feasible(current_a=1500)
    assert feasible is False


def test_ampacity_feasible_from_power_and_voltage(line1):
    """200 MW at 115 kV → ~1004 A, within [ampacity/3, ampacity] range — feasible."""
    feasible, _ = line1.is_ampacity_feasible(power_mw=200, voltage_kv=115)
    assert feasible is True


def test_ampacity_not_feasible_oversized(line1):
    """200 MW at 345 kV → ~335 A, far below ampacity/3 — line is oversized, not feasible."""
    feasible, message = line1.is_ampacity_feasible(power_mw=200, voltage_kv=345)
    assert feasible is False


def test_sag_feasible_with_max_sag(line1):
    """Sag at current within a generous max_sag limit — should be feasible."""
    feasible, _ = line1.is_sag_feasible(
        current_a=1300, max_sag_m=20, initial_tension_percentage=0.3
    )
    assert feasible is True


def test_sag_not_feasible_with_tight_limit(line1):
    """Sag at current exceeds a very tight max_sag limit — should not be feasible."""
    feasible, _ = line1.is_sag_feasible(
        current_a=1300, max_sag_m=5, initial_tension_percentage=0.3
    )
    assert feasible is False
