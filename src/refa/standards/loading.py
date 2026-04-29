from ..loading import Loading


def nesc_250b_heavy() -> Loading:
    return Loading(
        wind_ice_temperature_c=-5,
        pressure_pa=700,
        ice_thickness_m=0.025,
        ice_density_kg_per_m3=915,
        additive_loading_n_per_m=4.40,
    )


def nesc_250b_medium() -> Loading:
    return Loading(
        wind_ice_temperature_c=-5,
        pressure_pa=400,
        ice_thickness_m=0.013,
        ice_density_kg_per_m3=915,
        additive_loading_n_per_m=2.90,
    )


def nesc_250b_light() -> Loading:
    return Loading(
        wind_ice_temperature_c=0,
        pressure_pa=200,
        ice_thickness_m=0.006,
        ice_density_kg_per_m3=915,
        additive_loading_n_per_m=0.73,
    )


def nesc_250b_warmislands_low() -> Loading:
    return Loading(
        wind_ice_temperature_c=5,
        pressure_pa=200,
        ice_thickness_m=0.006,
        ice_density_kg_per_m3=915,
        additive_loading_n_per_m=0.73,
    )


def nesc_250b_warmislands_high() -> Loading:
    return Loading(
        wind_ice_temperature_c=5,
        pressure_pa=400,
        ice_thickness_m=0.013,
        ice_density_kg_per_m3=915,
        additive_loading_n_per_m=2.90,
    )