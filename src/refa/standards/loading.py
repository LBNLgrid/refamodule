from ..loading import LoadingMetric, LoadingImperial
from ..system_parameters import CF


def nesc_250b_heavy():
    return LoadingMetric(
        wind_ice_temperature_c=-5,
        pressure_pa=700,
        ice_thickness_m=0.025,
        ice_density_kg_per_m3=915,
        additive_loading_n_per_m=4.40,
    )


def nesc_250b_heavy_imperial():
    return LoadingImperial(
        wind_ice_temperature_f=CF.c_to_f(-5),
        pressure_lb_per_ft2=CF.pa_to_lb_per_ft2 * 700,
        ice_thickness_in=CF.m_to_in * 0.025,
        ice_density_lb_per_ft3=CF.kg_per_m3_to_lb_per_ft3 * 915,
        additive_loading_lbs_per_kft=CF.n_per_m_to_lbs_per_kft * 4.40,
    )


def nesc_250b_medium():
    return LoadingMetric(
        wind_ice_temperature_c=-5,
        pressure_pa=400,
        ice_thickness_m=0.013,
        ice_density_kg_per_m3=915,
        additive_loading_n_per_m=2.90,
    )


def nesc_250b_medium_imperial():
    return LoadingImperial(
        wind_ice_temperature_f=CF.c_to_f(-5),
        pressure_lb_per_ft2=CF.pa_to_lb_per_ft2 * 400,
        ice_thickness_m=CF.m_to_in * 0.013,
        ice_density_lb_per_ft3=CF.kg_per_m3_to_lb_per_ft3 * 915,
        additive_loading_lbs_per_kft=CF.n_per_m_to_lbs_per_kft * 2.90,
    )


def nesc_250b_light():
    return LoadingMetric(
        wind_ice_temperature_c=0,
        pressure_pa=200,
        ice_thickness_m=0.006,
        ice_density_kg_per_m3=915,
        additive_loading_n_per_m=0.73,
    )


def nesc_250b_light_imperial():
    return LoadingImperial(
        wind_ice_temperature_f=CF.c_to_f(0),
        pressure_per_ft2=CF.pa_to_lb_per_ft2 * 200,
        ice_thickness_in=CF.m_to_in * 0.006,
        ice_density_lb_per_ft3=CF.kg_per_m3_to_lb_per_ft3 * 915,
        additive_loading_lbs_per_kft=CF.n_per_m_to_lbs_per_kft * 0.73,
    )


def nesc_250b_warmislands_low():
    return LoadingMetric(
        wind_ice_temperature_c=5,
        pressure_pa=200,
        ice_thickness_m=0.006,
        ice_density_kg_per_m3=915,
        additive_loading_n_per_m=0.73,
    )


def nesc_250b_warmislands_low_imperial():
    return LoadingImperial(
        wind_ice_temperature_f=CF.c_to_f(5),
        pressure_lb_per_ft2=CF.pa_to_lb_per_ft2 * 200,
        ice_thickness_in=CF.m_to_in * 0.006,
        ice_density_lb_per_ft3=CF.kg_per_m3_to_lb_per_ft3 * 915,
        additive_loading_lbs_per_kft=CF.n_per_m_to_lbs_per_kft * 0.73,
    )


def nesc_250b_warmislands_high():
    return LoadingMetric(
        wind_ice_temperature_c=5,
        pressure_pa=400,
        ice_thickness_m=0.013,
        ice_density_kg_per_m3=915,
        additive_loading_n_per_m=2.90,
    )


def nesc_250b_warmislands_high_imperial():
    return LoadingImperial(
        wind_ice_temperature_f=CF.c_to_f(-5),
        pressure_lb_per_ft2=CF.pa_to_lb_per_ft2 * 400,
        ice_thickness_in=CF.m_to_in * 0.013,
        ice_density_lb_per_ft3=CF.kg_per_m3_to_lb_per_ft3 * 915,
        additive_loading_lbs_per_kft=CF.n_per_m_to_lbs_per_kft * 2.90,
    )