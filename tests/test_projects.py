"""Tests for project types and cost calculations."""
import pytest
from pytest import approx
from refa import Rebuild, Reconductoring, VoltageUpgrade, HVDC, Existing
from refa.defaults import acsr_795_0_drake, acss_795_0_cuckoo, accc_1035_dublin


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def rebuild_prj(line_design2, economics, structure_config_ac):
    return Rebuild(
        conductor_list=[acsr_795_0_drake(), acss_795_0_cuckoo(), accc_1035_dublin()],
        line_design=line_design2,
        economics=economics,
        power_mw=400,
        voltage_kv=230,
        structure_config=structure_config_ac,
    )


@pytest.fixture
def reconductoring_prj(line1, line2, economics):
    return Reconductoring(
        line_list=[line1, line2],
        economics=economics,
        power_mw=400,
        voltage_kv=230,
        structure_remaining_life=25,
    )


@pytest.fixture
def voltageupgrade_prj(line2, line1, economics):
    return VoltageUpgrade(
        line_list=[line2, line1],
        economics=economics,
        power_mw=400,
        voltage_kv=345,
        structure_remaining_life=0,
        conductor_remaining_life=0,
        cost_substations_upgrade_dol=2_000_000,
    )


@pytest.fixture
def hvdc_prj(line3, line2, economics, structure_config_dc):
    return HVDC(
        line_list=[line3, line2],
        economics=economics,
        power_mw=400,
        voltage_kv=500,
        structure_remaining_life=0,
        conductor_remaining_life=0,
        cost_converters_dol=3_000_000,
        nbr_dc_poles_per_circuit=2,
        structure_config=structure_config_dc,
    )


@pytest.fixture
def existing_prj(line1, economics):
    return Existing(
        line_list=[line1],
        economics=economics,
        power_mw=400,
        voltage_kv=230,
        structure_remaining_life=25,
        conductor_remaining_life=15,
    )


# ---------------------------------------------------------------------------
# Rebuild
# ---------------------------------------------------------------------------

def test_rebuild_total_costs_returns_list(rebuild_prj):
    result = rebuild_prj.total_costs(time_horizon=65)
    assert isinstance(result, list)
    assert len(result) == 2  # ACSS Cuckoo and ACCC Dublin pass ampacity feasibility


def test_rebuild_total_costs_npv_values(rebuild_prj):
    result = rebuild_prj.total_costs(time_horizon=65)
    npv_values = {r["conductor"]: r["npv_total_project_costs_mill_dol"] for r in result}
    assert npv_values["ACSS 795.0_CUCKOO"] == approx(12.157, rel=1e-3)
    assert npv_values["ACCC 1035_DUBLIN"] == approx(14.573, rel=1e-3)


def test_rebuild_result_keys(rebuild_prj):
    result = rebuild_prj.total_costs(time_horizon=65)
    assert "prj_name" in result[0]
    assert "conductor" in result[0]
    assert "npv_total_project_costs_mill_dol" in result[0]
    assert result[0]["prj_name"] == "Rebuild"


# ---------------------------------------------------------------------------
# Reconductoring
# ---------------------------------------------------------------------------

def test_reconductoring_total_costs_returns_list(reconductoring_prj):
    result = reconductoring_prj.total_costs(time_horizon=65)
    assert isinstance(result, list)
    assert len(result) >= 1


def test_reconductoring_npv_value(reconductoring_prj):
    result = reconductoring_prj.total_costs(time_horizon=65)
    npv_values = {r["conductor"]: r["npv_total_project_costs_mill_dol"] for r in result}
    assert npv_values["ACSS 795.0_CUCKOO"] == approx(1.734, rel=1e-3)


# ---------------------------------------------------------------------------
# VoltageUpgrade
# ---------------------------------------------------------------------------

def test_voltageupgrade_cost_attribute(voltageupgrade_prj):
    assert voltageupgrade_prj.cost_substations_upgrade_dol == 2_000_000


def test_voltageupgrade_cost_attribute_reassignment(voltageupgrade_prj):
    voltageupgrade_prj.cost_substations_upgrade_dol = 1_000_000
    assert voltageupgrade_prj.cost_substations_upgrade_dol == 1_000_000


# ---------------------------------------------------------------------------
# HVDC
# ---------------------------------------------------------------------------

def test_hvdc_cost_attribute(hvdc_prj):
    assert hvdc_prj.cost_converters_dol == 3_000_000


def test_hvdc_cost_attribute_reassignment(hvdc_prj):
    hvdc_prj.cost_converters_dol = 2_000_000
    assert hvdc_prj.cost_converters_dol == 2_000_000


# ---------------------------------------------------------------------------
# Existing
# ---------------------------------------------------------------------------

def test_existing_total_costs(existing_prj):
    result = existing_prj.total_costs(time_horizon=65)
    assert isinstance(result, list)
    assert len(result) >= 1


def test_existing_npv_value(existing_prj):
    result = existing_prj.total_costs(time_horizon=65)
    npv_values = {r["conductor"]: r["npv_total_project_costs_mill_dol"] for r in result}
    assert npv_values["ACSS 795.0_CUCKOO"] == approx(1.481, rel=1e-3)
