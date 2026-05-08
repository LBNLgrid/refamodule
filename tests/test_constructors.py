"""Tests for object construction and the + operator shorthand."""
import pytest
from pathlib import Path
from refa import LineDesign, Conductor, Line, Environment
from refa.defaults import (
    default_conductor,
    default_clear_environment,
    default_structure_config_ac,
    default_structure_config_dc,
    default_economics,
    acsr_795_0_drake,
    acss_795_0_cuckoo,
    accc_1035_dublin,
    load_conductors_from_csv,
)
from refa.standards import nesc_250b_heavy


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

def test_default_environment():
    env = default_clear_environment()
    assert isinstance(env, Environment)
    assert env.ambient_temperature_c == 25.0
    assert env.wind_speed_m_per_s == 1.0


def test_default_conductor():
    c = default_conductor()
    assert isinstance(c, Conductor)
    assert c.type == "ACSR"
    assert c.code == "556.5_DOVE"


def test_default_structure_config_ac(structure_config_ac):
    assert structure_config_ac is not None


def test_default_structure_config_dc(structure_config_dc):
    assert structure_config_dc is not None


def test_default_economics(economics):
    assert economics is not None


# ---------------------------------------------------------------------------
# Conductor database
# ---------------------------------------------------------------------------

def test_acsr_drake():
    c = acsr_795_0_drake()
    assert c.type == "ACSR"
    assert c.code == "795.0_DRAKE"


def test_acss_cuckoo():
    c = acss_795_0_cuckoo()
    assert c.type == "ACSS"
    assert c.code == "795.0_CUCKOO"
    assert c.max_temperature_c == 200.0


def test_accc_dublin():
    c = accc_1035_dublin()
    assert c.type == "ACCC"
    assert c.code == "1035_DUBLIN"


_DATA_DIR = Path(__file__).parent.parent / "data"
def test_load_conductors_from_csv():
    conductors = load_conductors_from_csv(str(_DATA_DIR / "conductors.csv"))
    assert len(conductors) > 0
    pelican = conductors.acsr_477_0_pelican()
    assert pelican.type == "ACSR"
    assert pelican.code == "477.0_PELICAN"


# ---------------------------------------------------------------------------
# Conductor manual construction
# ---------------------------------------------------------------------------

def test_conductor_manual_construction():
    c = Conductor(
        type="ACSR",
        code="266.8_PARTRIDGE",
        area_mm2=157.0,
        diameter_mm=16.0,
        weight_n_per_m=5.36,
        conductor_rts_kn=50.26,
        cost_dol_per_km=2410.8,
        installation_dol_per_km=3368.56,
        accessories_dol_per_km=862.64,
        str_costs_dol=0.0,
        temp_dc_c=20.0,
        temp_low_c=25.0,
        temp_high_c=75.0,
        max_temperature_c=100.0,
        res_dc_ohm_per_m=0.000209,
        res_low_ohm_per_m=0.000209,
        res_high_ohm_per_m=0.000256,
        elastic_modulus_gpa=75.5,
        coeff_thermal_expan_per_c=1.92e-05,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )
    assert c.type == "ACSR"
    assert c.diameter_mm == 16.0


# ---------------------------------------------------------------------------
# LineDesign construction
# ---------------------------------------------------------------------------

def test_line_design_construction(line_design1):
    assert line_design1.nbr_circuits == 1
    assert line_design1.nbr_bundles == 3
    assert line_design1.length_km == 10.0
    assert line_design1.avg_span_m == 250.0
    assert line_design1.max_span_m == 300.0
    assert line_design1.nbr_structures == 41


def test_line_design2_construction(line_design2):
    assert line_design2.length_km == 30.0
    assert line_design2.avg_span_m == 300.0


# ---------------------------------------------------------------------------
# Line construction
# ---------------------------------------------------------------------------

def test_line_constructor(line_design1, conductor_acss):
    line = Line(line_design=line_design1, conductor=conductor_acss)
    assert line.conductor.code == "795.0_CUCKOO"
    assert line.line_design.length_km == 10.0


def test_line_design_plus_conductor(line_design2, conductor_acsr):
    line = line_design2 + conductor_acsr
    assert isinstance(line, Line)
    assert line.conductor.code == "795.0_DRAKE"


def test_conductor_plus_line_design(conductor_accc, line_design1):
    line = conductor_accc + line_design1
    assert isinstance(line, Line)
    assert line.conductor.code == "1035_DUBLIN"


# ---------------------------------------------------------------------------
# NESC loading
# ---------------------------------------------------------------------------

def test_nesc_250b_heavy(loading):
    assert loading.wind_ice_temperature_c == -5.0
    assert loading.ice_thickness_m == 0.025
