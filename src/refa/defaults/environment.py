from ..environment import EnvironmentMetric, EnvironmentImperial
import datetime as dt


def default_clear_environment():
    return EnvironmentMetric(
        date=dt.date.today(),
        latitude=45.0,
        elevation_m=100.0,
        wind_speed_m_per_s=1.0,
        wind_angle=90,
        cw_angle_direction_rel_to_north=90,
        hour=12,
        ambient_temperature_c=25.0,
        atmosphere= _clear_atmosphere(),
        weather_correction_factor=1.0, 
        rugosity_coefficient=0.82
    )

def default_industrial_environment():
    return EnvironmentMetric(
        date=dt.date.today(),
        latitude=45.0,
        elevation_m=100.0,
        wind_speed_m_per_s=1.0,
        wind_angle=90,
        cw_angle_direction_rel_to_north=90,
        hour=12,
        ambient_temperature_c=25.0,
        atmosphere= _industrial_atmosphere(),
        weather_correction_factor=1.0,
        rugosity_coefficient=0.82
    )


def default_clear_environment_imperial():
    return EnvironmentImperial(
        date=dt.date.today(),
        latitude=45,
        elevation_ft=328,
        wind_speed_mph=2.24,
        wind_angle=0,
        cw_angle_direction_rel_to_north=0,
        hour=12,
        ambient_temperature_f=77,
        atmosphere=_clear_atmosphere(),
        weather_correction_factor=1.0,
        rugosity_coefficient=0.82
    )


def default_industrial_environment_imperial():
    return EnvironmentImperial(
        date=dt.date.today(),
        latitude=45,
        elevation_ft=328,
        wind_speed_mph=2.24,
        wind_angle=0,
        cw_angle_direction_rel_to_north=0,
        hour=12,
        ambient_temperature_f=77,
        atmosphere=_industrial_atmosphere(),
        weather_correction_factor=1.0,
        rugosity_coefficient=0.82
    )


def _clear_atmosphere():
    return  {"A": -42.2391,
             "B": 63.8044,
             "C": -1.9220,
             "D": 3.46921e-2,
             "E": -3.61118e-4,
             "F": 1.94318e-6,
             "G": -4.07608e-9}

def _industrial_atmosphere():
    return {"A": 53.1821,
            "B": 14.2110,
            "C": 6.6138e-1,
            "D": -3.1658e-2,
            "E": 5.4654e-4,
            "F": -4.3446e-6,
            "G": 1.3236e-8}

