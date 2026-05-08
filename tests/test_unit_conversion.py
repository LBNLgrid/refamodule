"""Tests for the unit conversion system.

Covers:
- CF conversion factor constants (round-trips and known values)
- Imperial constructor classes (ConductorImperial, EnvironmentImperial,
  LineDesignImperial, LoadingImperial, StructureConfig*imperial)
- UnitSystem (is_metric / is_imperial)
- ParameterAccess.get_parameter in both unit systems
- Default imperial factory functions
"""
import math
import pytest
from pytest import approx

from refa.system_parameters.parameter_access import CF, UnitSystem
from refa.conductor import ConductorMetric, ConductorImperial
from refa.environment import EnvironmentMetric, EnvironmentImperial
from refa.line_design import LineDesignMetric, LineDesignImperial
from refa.loading import LoadingMetric, LoadingImperial
from refa.structure_config import (
    StructureConfigACmetric, StructureConfigACimperial,
    StructureConfigDCmetric, StructureConfigDCimperial,
)
from refa.defaults import (
    default_conductor, default_conductor_imperial,
    default_clear_environment, default_clear_environment_imperial,
    default_structure_config_ac, default_structure_config_ac_imperial,
    default_structure_config_dc, default_structure_config_dc_imperial,
)
from refa.standards import nesc_250b_heavy, nesc_250b_heavy_imperial


# ---------------------------------------------------------------------------
# CF — Conversion factor constants
# ---------------------------------------------------------------------------

class TestCFConstants:
    """Verify key conversion factors via known values and round-trips."""

    def test_temperature_freezing(self):
        assert CF.c_to_f(0) == approx(32.0)

    def test_temperature_boiling(self):
        assert CF.c_to_f(100) == approx(212.0)

    def test_temperature_round_trip(self):
        for t in [-40, 0, 25, 100, 200]:
            assert CF.f_to_c(CF.c_to_f(t)) == approx(t, abs=1e-9)

    def test_length_ft_m_round_trip(self):
        assert CF.ft_to_m * CF.m_to_ft == approx(1.0, rel=1e-6)

    def test_length_km_mile_round_trip(self):
        assert CF.km_to_mile * CF.mile_to_km == approx(1.0, rel=1e-6)

    def test_length_mm_in_round_trip(self):
        assert CF.mm_to_in * CF.in_to_mm == approx(1.0, rel=1e-6)

    def test_area_mm2_kcmil_round_trip(self):
        assert CF.mm2_to_kcmil * CF.kcmil_to_mm2 == approx(1.0, rel=1e-3)

    def test_force_kn_kip_round_trip(self):
        assert CF.kn_to_kip * CF.kip_to_kn == approx(1.0, rel=1e-6)

    def test_modulus_gpa_ksi_round_trip(self):
        assert CF.gpa_to_ksi * CF.ksi_to_gpa == approx(1.0, rel=1e-6)

    def test_pressure_round_trip(self):
        assert CF.pa_to_lb_per_ft2 * CF.lb_per_ft2_to_pa == approx(1.0, rel=1e-6)

    def test_speed_mph_m_per_s_round_trip(self):
        assert CF.mph_to_m_per_s * CF.m_per_s_to_mph == approx(1.0, rel=1e-6)

    def test_one_foot_in_meters(self):
        assert CF.ft_to_m == approx(0.3048, rel=1e-6)

    def test_one_inch_in_mm(self):
        assert CF.in_to_mm == approx(25.4, rel=1e-6)

    def test_one_mile_in_km(self):
        assert CF.mile_to_km == approx(1.60934, rel=1e-4)


# ---------------------------------------------------------------------------
# ConductorImperial
# ---------------------------------------------------------------------------

class TestConductorImperial:
    """ConductorImperial must return a ConductorMetric with correctly converted fields."""

    @pytest.fixture
    def metric(self):
        """Reference metric conductor (ACSR 795 DRAKE)."""
        from refa.defaults import acsr_795_0_drake
        return acsr_795_0_drake()

    @pytest.fixture
    def imperial(self, metric):
        """Same conductor constructed via imperial inputs."""
        return ConductorImperial(
            type=metric.type,
            code=metric.code,
            area_kcmil=metric.area_mm2 * CF.mm2_to_kcmil,
            diameter_in=metric.diameter_mm * CF.mm_to_in,
            weight_lbs_per_kft=metric.weight_n_per_m * CF.n_per_m_to_lbs_per_kft,
            conductor_rts_kip=metric.conductor_rts_kn * CF.kn_to_kip,
            temp_dc_f=CF.c_to_f(metric.temp_dc_c),
            temp_low_f=CF.c_to_f(metric.temp_low_c),
            temp_high_f=CF.c_to_f(metric.temp_high_c),
            max_temperature_f=CF.c_to_f(metric.max_temperature_c),
            res_dc_ohm_per_mile=metric.res_dc_ohm_per_m * CF.mile_to_m,
            res_low_ohm_per_mile=metric.res_low_ohm_per_m * CF.mile_to_m,
            res_high_ohm_per_mile=metric.res_high_ohm_per_m * CF.mile_to_m,
            elastic_modulus_ksi=metric.elastic_modulus_gpa * CF.gpa_to_ksi,
            coeff_thermal_expan_per_f=metric.coeff_thermal_expan_per_c * 5 / 9,
            cost_dol_per_kft=metric.cost_dol_per_km / CF.m_to_ft,
            installation_dol_per_kft=metric.installation_dol_per_km / CF.m_to_ft,
            accessories_dol_per_kft=metric.accessories_dol_per_km / CF.m_to_ft,
        )

    def test_returns_conductor_metric(self, imperial):
        assert isinstance(imperial, ConductorMetric)

    def test_area(self, metric, imperial):
        assert imperial.area_mm2 == approx(metric.area_mm2, rel=1e-3)

    def test_diameter(self, metric, imperial):
        assert imperial.diameter_mm == approx(metric.diameter_mm, rel=1e-3)

    def test_weight(self, metric, imperial):
        assert imperial.weight_n_per_m == approx(metric.weight_n_per_m, rel=1e-3)

    def test_rts(self, metric, imperial):
        assert imperial.conductor_rts_kn == approx(metric.conductor_rts_kn, rel=1e-3)

    def test_temperature_dc(self, metric, imperial):
        assert imperial.temp_dc_c == approx(metric.temp_dc_c, abs=1e-6)

    def test_temperature_max(self, metric, imperial):
        assert imperial.max_temperature_c == approx(metric.max_temperature_c, abs=1e-6)

    def test_resistance(self, metric, imperial):
        assert imperial.res_low_ohm_per_m == approx(metric.res_low_ohm_per_m, rel=1e-3)

    def test_elastic_modulus(self, metric, imperial):
        assert imperial.elastic_modulus_gpa == approx(metric.elastic_modulus_gpa, rel=1e-3)

    def test_thermal_expansion(self, metric, imperial):
        assert imperial.coeff_thermal_expan_per_c == approx(metric.coeff_thermal_expan_per_c, rel=1e-3)

    def test_cost(self, metric, imperial):
        assert imperial.cost_dol_per_km == approx(metric.cost_dol_per_km, rel=1e-3)


# ---------------------------------------------------------------------------
# EnvironmentImperial
# ---------------------------------------------------------------------------

class TestEnvironmentImperial:
    """EnvironmentImperial must return an EnvironmentMetric with correctly converted fields."""

    @pytest.fixture
    def env_imp(self):
        return EnvironmentImperial(
            latitude=45,
            elevation_ft=100 / CF.ft_to_m,   # 100 m → ft
            wind_speed_mph=1.0 / CF.mph_to_m_per_s,   # 1 m/s → mph
            wind_angle=90,
            cw_angle_direction_rel_to_north=90,
            hour=12,
            ambient_temperature_f=CF.c_to_f(25.0),
            atmosphere={"A": -42.2391, "B": 63.8044, "C": -1.9220,
                        "D": 3.46921e-2, "E": -3.61118e-4,
                        "F": 1.94318e-6, "G": -4.07608e-9},
        )

    def test_returns_environment_metric(self, env_imp):
        assert isinstance(env_imp, EnvironmentMetric)

    def test_elevation(self, env_imp):
        assert env_imp.elevation_m == approx(100.0, rel=1e-3)

    def test_wind_speed(self, env_imp):
        assert env_imp.wind_speed_m_per_s == approx(1.0, rel=1e-3)

    def test_ambient_temperature(self, env_imp):
        assert env_imp.ambient_temperature_c == approx(25.0, abs=1e-4)


# ---------------------------------------------------------------------------
# LineDesignImperial
# ---------------------------------------------------------------------------

class TestLineDesignImperial:
    """LineDesignImperial must return a LineDesignMetric with correctly converted fields."""

    @pytest.fixture
    def env(self):
        return default_clear_environment()

    @pytest.fixture
    def ld_imp(self, env):
        return LineDesignImperial(
            environment=env,
            nbr_circuits=1,
            nbr_bundles=3,
            nbr_conds_per_bundle=1,
            length_mile=30 / CF.mile_to_km,    # 30 km → miles
            avg_span_ft=300 / CF.ft_to_m,       # 300 m → ft
            max_span_ft=300 / CF.ft_to_m,
            max_sag_ft=10.0 / CF.ft_to_m,       # 10 m → ft
        )

    def test_returns_line_design_metric(self, ld_imp):
        assert isinstance(ld_imp, LineDesignMetric)

    def test_length(self, ld_imp):
        assert ld_imp.length_km == approx(30.0, rel=1e-3)

    def test_avg_span(self, ld_imp):
        assert ld_imp.avg_span_m == approx(300.0, rel=1e-3)

    def test_max_span(self, ld_imp):
        assert ld_imp.max_span_m == approx(300.0, rel=1e-3)

    def test_max_sag(self, ld_imp):
        assert ld_imp.max_sag_m == approx(10.0, rel=1e-3)

    def test_nbr_structures_auto_calculated(self, ld_imp):
        assert ld_imp.nbr_structures == math.ceil(30_000 / 300) + 1  # 101


# ---------------------------------------------------------------------------
# LoadingImperial
# ---------------------------------------------------------------------------

class TestLoadingImperial:
    """LoadingImperial must return a LoadingMetric with correctly converted fields."""

    @pytest.fixture
    def loading_metric(self):
        return nesc_250b_heavy()

    @pytest.fixture
    def loading_imp(self):
        return nesc_250b_heavy_imperial()

    def test_returns_loading_metric(self, loading_imp):
        assert isinstance(loading_imp, LoadingMetric)

    def test_temperature(self, loading_metric, loading_imp):
        assert loading_imp.wind_ice_temperature_c == approx(loading_metric.wind_ice_temperature_c, abs=0.1)

    def test_ice_thickness(self, loading_metric, loading_imp):
        assert loading_imp.ice_thickness_m == approx(loading_metric.ice_thickness_m, rel=1e-3)

    def test_pressure(self, loading_metric, loading_imp):
        assert loading_imp.pressure_pa == approx(loading_metric.pressure_pa, rel=1e-2)


# ---------------------------------------------------------------------------
# StructureConfig imperial classes
# ---------------------------------------------------------------------------

class TestStructureConfigImperial:
    """Imperial structure config constructors must produce equivalent metric values."""

    def test_ac_returns_metric_type(self):
        cfg = default_structure_config_ac_imperial()
        assert isinstance(cfg, StructureConfigACmetric)

    def test_dc_returns_metric_type(self):
        cfg = default_structure_config_dc_imperial()
        assert isinstance(cfg, StructureConfigDCmetric)

    def test_ac_distances(self):
        cfg = default_structure_config_ac_imperial()
        expected_m = 12 * CF.ft_to_m
        assert cfg.distance_a_b_m == approx(expected_m, rel=1e-6)
        assert cfg.distance_a_c_m == approx(expected_m, rel=1e-6)
        assert cfg.distance_b_c_m == approx(expected_m, rel=1e-6)

    def test_ac_height(self):
        cfg = default_structure_config_ac_imperial()
        assert cfg.structure_height_m == approx(75 * CF.ft_to_m, rel=1e-6)

    def test_dc_pole_distance(self):
        cfg = default_structure_config_dc_imperial()
        assert cfg.distance_pos_neg_poles_m == approx(12 * CF.ft_to_m, rel=1e-6)

    def test_dc_height(self):
        cfg = default_structure_config_dc_imperial()
        assert cfg.structure_height_m == approx(75 * CF.ft_to_m, rel=1e-6)

    def test_ac_custom_values(self):
        cfg = StructureConfigACimperial(
            distance_a_b_ft=10, distance_a_c_ft=20, distance_b_c_ft=15,
            structure_height_ft=80,
        )
        assert cfg.distance_a_b_m == approx(10 * CF.ft_to_m, rel=1e-6)
        assert cfg.distance_a_c_m == approx(20 * CF.ft_to_m, rel=1e-6)
        assert cfg.structure_height_m == approx(80 * CF.ft_to_m, rel=1e-6)

    def test_dc_custom_values(self):
        cfg = StructureConfigDCimperial(distance_pos_neg_poles_ft=15, structure_height_ft=60)
        assert cfg.distance_pos_neg_poles_m == approx(15 * CF.ft_to_m, rel=1e-6)
        assert cfg.structure_height_m == approx(60 * CF.ft_to_m, rel=1e-6)


# ---------------------------------------------------------------------------
# UnitSystem
# ---------------------------------------------------------------------------

class TestUnitSystem:
    """UnitSystem should read from config and expose is_metric / is_imperial."""

    def test_default_is_metric(self):
        # config.toml sets unit_system = "metric"
        assert UnitSystem.is_metric() is True

    def test_is_metric_and_is_imperial_are_complementary(self):
        assert UnitSystem.is_metric() != UnitSystem.is_imperial()

    def test_set_and_restore(self):
        original = "metric" if UnitSystem.is_metric() else "imperial"
        try:
            UnitSystem.set("imperial")
            assert UnitSystem.is_imperial() is True
            assert UnitSystem.is_metric() is False
        finally:
            UnitSystem.set(original)

    def test_set_metric(self):
        original = "metric" if UnitSystem.is_metric() else "imperial"
        try:
            UnitSystem.set("imperial")
            UnitSystem.set("metric")
            assert UnitSystem.is_metric() is True
        finally:
            UnitSystem.set(original)


# ---------------------------------------------------------------------------
# ParameterAccess.get_parameter
# ---------------------------------------------------------------------------

class TestParameterAccess:
    """get_parameter must return (value, unit_label) in the requested unit system."""

    @pytest.fixture
    def conductor(self):
        from refa.defaults import acsr_795_0_drake
        return acsr_795_0_drake()

    def test_get_parameter_returns_tuple(self, conductor):
        result = conductor.get_parameter("area")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_get_area_metric(self, conductor):
        value, unit = conductor.get_parameter("area", unit_system="metric")
        assert value == approx(conductor.area_mm2, rel=1e-6)
        assert "mm" in unit

    def test_get_area_imperial(self, conductor):
        value, unit = conductor.get_parameter("area", unit_system="imperial")
        assert value == approx(conductor.area_mm2 * CF.mm2_to_kcmil, rel=1e-3)
        assert "kcmil" in unit.lower()

    def test_get_diameter_metric(self, conductor):
        value, unit = conductor.get_parameter("diameter", unit_system="metric")
        assert value == approx(conductor.diameter_mm, rel=1e-6)

    def test_get_diameter_imperial(self, conductor):
        value, unit = conductor.get_parameter("diameter", unit_system="imperial")
        assert value == approx(conductor.diameter_mm * CF.mm_to_in, rel=1e-3)

    def test_get_max_temperature_metric(self, conductor):
        value, unit = conductor.get_parameter("max_temperature", unit_system="metric")
        assert value == approx(conductor.max_temperature_c, rel=1e-6)
        assert "c" in unit.lower()

    def test_get_max_temperature_imperial(self, conductor):
        value, unit = conductor.get_parameter("max_temperature", unit_system="imperial")
        assert value == approx(CF.c_to_f(conductor.max_temperature_c), rel=1e-3)
        assert "f" in unit.lower()

    def test_get_cost_metric(self, conductor):
        value, unit = conductor.get_parameter("cost", unit_system="metric")
        assert value == approx(conductor.cost_dol_per_km, rel=1e-6)

    def test_get_cost_imperial(self, conductor):
        value, unit = conductor.get_parameter("cost", unit_system="imperial")
        # cost_dol_per_kft = cost_dol_per_km / m_to_ft (since 1 km = m_to_ft kft)
        expected = conductor.cost_dol_per_km * CF.ft_to_m
        assert value == approx(expected, rel=1e-3)

    def test_environment_get_elevation_metric(self):
        env = default_clear_environment()
        value, unit = env.get_parameter("elevation", unit_system="metric")
        assert value == approx(100.0, rel=1e-6)
        assert "m" in unit

    def test_environment_get_elevation_imperial(self):
        env = default_clear_environment()
        value, unit = env.get_parameter("elevation", unit_system="imperial")
        assert value == approx(100.0 * CF.m_to_ft, rel=1e-3)
        assert "ft" in unit.lower()


# ---------------------------------------------------------------------------
# Default imperial factory functions
# ---------------------------------------------------------------------------

class TestDefaultImperialFunctions:
    """Imperial default functions must return the correct metric model instances."""

    def test_default_conductor_imperial_type(self):
        c = default_conductor_imperial()
        assert isinstance(c, ConductorMetric)

    def test_default_conductor_imperial_code(self):
        c = default_conductor_imperial()
        assert c.code == "556.5_DOVE"
        assert c.type == "ACSR"

    def test_default_clear_environment_imperial_type(self):
        env = default_clear_environment_imperial()
        assert isinstance(env, EnvironmentMetric)

    def test_default_clear_environment_imperial_elevation(self):
        env = default_clear_environment_imperial()
        # 328 ft → m
        assert env.elevation_m == approx(328 * CF.ft_to_m, rel=1e-3)

    def test_default_clear_environment_imperial_temperature(self):
        env = default_clear_environment_imperial()
        # 77 °F → 25 °C
        assert env.ambient_temperature_c == approx(25.0, abs=0.01)

    def test_default_clear_environment_imperial_wind_speed(self):
        env = default_clear_environment_imperial()
        # 2.24 mph → m/s
        assert env.wind_speed_m_per_s == approx(2.24 * CF.mph_to_m_per_s, rel=1e-3)

    def test_default_structure_config_ac_imperial_type(self):
        cfg = default_structure_config_ac_imperial()
        assert isinstance(cfg, StructureConfigACmetric)

    def test_default_structure_config_dc_imperial_type(self):
        cfg = default_structure_config_dc_imperial()
        assert isinstance(cfg, StructureConfigDCmetric)
