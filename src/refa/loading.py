from pydantic import BaseModel, Field
from .system_parameters import ParameterAccess, CF


class LoadingMetric(BaseModel, ParameterAccess):
    wind_ice_temperature_c:   float = Field(..., ge=-60, le=60)    
    pressure_pa:              float = Field(..., ge=0)                           
    ice_thickness_m:          float = Field(..., ge=0)                                
    ice_density_kg_per_m3:    float = Field(..., ge=0)                                
    additive_loading_n_per_m: float = Field(..., ge=0)                                


class LoadingImperial:
    def __new__(cls,
                wind_ice_temperature_f:    float,
                pressure_lb_per_ft2:       float = 0,
                ice_thickness_in:          float = 0,
                ice_density_lb_per_ft3:    float = 0,
                additive_loading_lbs_per_kft: float = 0) -> LoadingMetric:
        return LoadingMetric(
            wind_ice_temperature_c    = (wind_ice_temperature_f - 32) * 5 / 9,
            pressure_pa               = pressure_lb_per_ft2           * CF.lb_per_ft2_to_pa,
            ice_thickness_m           = ice_thickness_in              * CF.in_to_mm / 1000,
            ice_density_kg_per_m3     = ice_density_lb_per_ft3        * CF.lb_per_ft3_to_kg_per_m3,
            additive_loading_n_per_m  = additive_loading_lbs_per_kft  * CF.lbs_per_kft_to_n_per_m,
        )