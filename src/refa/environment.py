import datetime as dt
from pydantic import BaseModel, Field
from .system_parameters import ParameterAccess, CF


class EnvironmentMetric(BaseModel, ParameterAccess):
    date:                            dt.date = Field(default_factory=dt.date.today)
    latitude:                        float   = Field(..., ge=-90, le=90)        
    elevation_m:                     float   = Field(..., ge=0)                 
    wind_speed_m_per_s:              float   = Field(..., ge=0)                 
    wind_angle:                      int     = Field(..., ge=0, le=90)          
    cw_angle_direction_rel_to_north: int     = Field(..., ge=0, le=90)          
    hour:                            int     = Field(..., ge=0, le=24)
    atmosphere:                      dict    = Field(...)
    ambient_temperature_c:           float   = Field(..., ge=-60, le=40)        
    weather_correction_factor:       float   = Field(1.0,  gt=0)
    rugosity_coefficient:            float   = Field(0.82, gt=0)


class EnvironmentImperial:
    def __new__(cls,
                latitude:                        float,
                elevation_ft:                    float,
                wind_speed_mph:                  float,
                wind_angle:                      int,
                cw_angle_direction_rel_to_north: int,
                hour:                            int,
                atmosphere:                      dict,
                ambient_temperature_f:           float,
                date:                            dt.date = None,
                weather_correction_factor:       float   = 1.0,
                rugosity_coefficient:            float   = 0.82) -> EnvironmentMetric:
        return EnvironmentMetric(
            date                            = date or dt.date.today(),
            latitude                        = latitude,
            elevation_m                     = elevation_ft        * CF.ft_to_m,
            wind_speed_m_per_s              = wind_speed_mph       * CF.mph_to_m_per_s,
            wind_angle                      = wind_angle,
            cw_angle_direction_rel_to_north = cw_angle_direction_rel_to_north,
            hour                            = hour,
            atmosphere                      = atmosphere,
            ambient_temperature_c           = (ambient_temperature_f - 32) * 5 / 9,
            weather_correction_factor       = weather_correction_factor,
            rugosity_coefficient            = rugosity_coefficient,
        )