"""Tests for Line technical calculation methods.

Expected values are taken from the module with the current default environment
(wind_angle=90, cw_angle_direction_rel_to_north=90, pinned date 2026-04-28).
A relative tolerance of 0.1% (rel=1e-3) is used for floating-point comparisons.
"""
import pytest
from pytest import approx


# ---------------------------------------------------------------------------
# Temperature & resistance
# ---------------------------------------------------------------------------

def test_temperature_at_current(line1):
    result, _ = line1.temperature_at_current(current_a=1400)
    assert result == approx(122.800, rel=1e-3)


def test_resistance_at_current(line1):
    result, _ = line1.resistance_at_current(current_a=1400)
    assert result == approx(1.010e-04, rel=1e-3)


def test_temperature_at_power_and_voltage(line1):
    result, _ = line1.temperature_at_current(power_mw=550, voltage_kv=345)
    assert result == approx(65.942, rel=1e-3)


def test_resistance_at_power_and_voltage(line1):
    result, _ = line1.resistance_at_current(power_mw=550, voltage_kv=345)
    assert result == approx(8.351e-05, rel=1e-3)


# ---------------------------------------------------------------------------
# Ampacity
# ---------------------------------------------------------------------------

def test_ampacity(line1):
    result, _ = line1.ampacity_at_environment()
    assert result == approx(1780.739, rel=1e-3)


# ---------------------------------------------------------------------------
# Sag
# ---------------------------------------------------------------------------

def test_sag_at_current(line1):
    result, _ = line1.sag_at_current(current_a=1400, initial_tension_percentage=0.2)
    assert result == approx(11.780, rel=1e-3)


def test_sag_at_temperature(line1):
    result, _ = line1.sag_at_temperature(
        temp_at_current_c=85, initial_tension_percentage=0.2
    )
    assert result == approx(10.826, rel=1e-3)


def test_sag_at_loading(line1, loading):
    result, _ = line1.sag_at_loading(
        loading_conditions=loading, initial_tension_percentage=0.2
    )
    assert result == approx(11.552, rel=1e-3)


def test_sag_at_power_and_voltage(line1):
    result, _ = line1.sag_at_power_and_voltage(
        power_mw=500, voltage_kv=230, initial_tension_percentage=0.2
    )
    assert isinstance(result, float)
    assert result > 0


# ---------------------------------------------------------------------------
# Corona
# ---------------------------------------------------------------------------

def test_corona_inception_voltage(line1, structure_config_ac):
    result, _ = line1.corona_inception_voltage(structure_config=structure_config_ac)
    assert result == approx(230.184, rel=1e-3)


def test_corona_voltage_gradient(line1, structure_config_ac):
    result, _ = line1.corona_voltage_gradient(structure_config=structure_config_ac)
    assert result == approx(29.075, rel=1e-3)


# ---------------------------------------------------------------------------
# Losses
# ---------------------------------------------------------------------------

def test_resistive_line_losses_from_current(line1):
    result, _ = line1.resistive_line_losses(current_a=1400, load_factor=0.6)
    assert result == approx(2.248, rel=1e-3)


def test_resistive_line_losses_with_congestion(line1):
    result, _ = line1.resistive_line_losses_considering_congestion(
        power_mw=550, voltage_kv=230, load_factor=0.6
    )
    assert result == approx(2.166, rel=1e-3)


def test_corona_discharge_losses_ac(line1, structure_config_ac):
    result, _ = line1.corona_discharge_losses(
        voltage_kv=345, load_factor=0.6, structure_config=structure_config_ac
    )
    assert result == approx(0.622, rel=1e-3)


def test_corona_discharge_losses_dc(line1, structure_config_dc):
    result, _ = line1.corona_discharge_losses(
        voltage_kv=345, load_factor=0.6, structure_config=structure_config_dc, is_hvdc=True
    )
    assert result == approx(0.02728, rel=1e-3)


# ---------------------------------------------------------------------------
# Congestion  (ampacity ~1780 A, so 1500 A and 700 MW/230 kV are both feasible)
# ---------------------------------------------------------------------------

def test_congestion_from_current(line1):
    result, _ = line1.congestion(current_a=1500, voltage_kv=230)
    assert result == approx(0.0, abs=1e-6)


def test_congestion_from_power(line1):
    result, _ = line1.congestion(power_mw=700, voltage_kv=230)
    assert result == approx(0.0, abs=1e-6)


# ---------------------------------------------------------------------------
# Overall technical performance
# ---------------------------------------------------------------------------

def test_overall_performance_current_only(line1):
    result = line1.overall_technical_performance(current_a=1500)
    assert "ampacity" in result
    assert "sag" in result
    assert result["ampacity"][0] == approx(1780.739, rel=1e-3)


def test_overall_performance_power_and_voltage(line1):
    result = line1.overall_technical_performance(power_mw=500, voltage_kv=230)
    assert "ampacity" in result
    assert "sag" in result
    assert "congestion" in result


def test_overall_performance_with_losses(line1):
    result = line1.overall_technical_performance(current_a=1500, load_factor=0.6)
    assert "resistive_losses" in result
    assert result["resistive_losses"][0] == approx(2.716, rel=1e-3)


def test_overall_performance_with_corona(line1, structure_config_ac):
    result = line1.overall_technical_performance(
        current_a=1500,
        voltage_kv=230,
        load_factor=0.6,
        structure_config=structure_config_ac,
    )
    assert "corona_inception_voltage" in result
    assert "corona_losses" in result
    assert result["corona_inception_voltage"][0] == approx(230.184, rel=1e-3)
