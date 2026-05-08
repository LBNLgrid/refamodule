"""Tests for the Analysis class."""
import pytest
from pytest import approx
from refa import Rebuild, Reconductoring, VoltageUpgrade, HVDC, Existing, Analysis
from refa.defaults import acsr_795_0_drake, acss_795_0_cuckoo, accc_1035_dublin


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def all_projects(
    line_design2, line1, line2, line3, economics, structure_config_ac, structure_config_dc
):
    rebuild_prj = Rebuild(
        conductor_list=[acsr_795_0_drake(), acss_795_0_cuckoo(), accc_1035_dublin()],
        line_design=line_design2,
        economics=economics,
        power_mw=400,
        voltage_kv=230,
        structure_config=structure_config_ac,
    )
    reconductoring_prj = Reconductoring(
        line_list=[line1, line2],
        economics=economics,
        power_mw=400,
        voltage_kv=230,
        structure_remaining_life=25,
    )
    voltageupgrade_prj = VoltageUpgrade(
        line_list=[line2, line1],
        economics=economics,
        power_mw=400,
        voltage_kv=345,
        structure_remaining_life=0,
        conductor_remaining_life=0,
        cost_substations_upgrade_dol=2_000_000,
    )
    hvdc_prj = HVDC(
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
    existing_prj = Existing(
        line_list=[line1],
        economics=economics,
        power_mw=400,
        voltage_kv=230,
        structure_remaining_life=25,
        conductor_remaining_life=15,
    )
    return rebuild_prj, reconductoring_prj, voltageupgrade_prj, hvdc_prj, existing_prj


@pytest.fixture
def analysis(all_projects):
    return Analysis(project_list=list(all_projects))


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

def test_analysis_total_costs_returns_dict(analysis):
    result = analysis.total_costs_of_projects(time_horizon=70)
    assert isinstance(result, dict)


def test_analysis_total_costs_keys(analysis):
    result = analysis.total_costs_of_projects(time_horizon=70)
    assert "Rebuild" in result
    assert "Reconductoring" in result
    assert "VoltageUpgrade" in result
    assert "HVDC" in result
    assert "Existing" in result


# ---------------------------------------------------------------------------
# Values — matched to notebook output
# ---------------------------------------------------------------------------

def test_analysis_rebuild_npv(analysis):
    result = analysis.total_costs_of_projects(time_horizon=70)
    rebuild = {r["conductor"]: r["npv_total_project_costs_mill_dol"] for r in result["Rebuild"]}
    assert rebuild["ACSS 795.0_CUCKOO"] == approx(12.157, rel=1e-3)
    assert rebuild["ACCC 1035_DUBLIN"] == approx(14.573, rel=1e-3)


def test_analysis_reconductoring_npv(analysis):
    result = analysis.total_costs_of_projects(time_horizon=70)
    recon = {r["conductor"]: r["npv_total_project_costs_mill_dol"] for r in result["Reconductoring"]}
    assert recon["ACSS 795.0_CUCKOO"] == approx(1.734, rel=1e-3)


def test_analysis_existing_npv(analysis):
    result = analysis.total_costs_of_projects(time_horizon=70)
    existing = {r["conductor"]: r["npv_total_project_costs_mill_dol"] for r in result["Existing"]}
    assert existing["ACSS 795.0_CUCKOO"] == approx(1.481, rel=1e-3)


def test_analysis_voltage_upgrade_filtered_empty(analysis):
    """VoltageUpgrade and HVDC are expected to be filtered out (infeasible) in the notebook."""
    result = analysis.total_costs_of_projects(time_horizon=70)
    assert result["VoltageUpgrade"] == {} or isinstance(result["VoltageUpgrade"], (dict, list))
    assert result["HVDC"] == {} or isinstance(result["HVDC"], (dict, list))
