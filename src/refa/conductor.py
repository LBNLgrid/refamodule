from pydantic import BaseModel, Field
from .system_parameters import ParameterAccess, CF


class ConductorMetric(BaseModel, ParameterAccess):
    type:                        str
    code:                        str
    area_mm2:                    float = Field(..., gt=0)
    diameter_mm:                 float = Field(..., gt=0)
    weight_n_per_m:              float = Field(..., gt=0)
    conductor_rts_kn:            float = Field(..., gt=0)
    temp_dc_c:                   float = Field(..., ge=0, le=100)
    temp_low_c:                  float = Field(..., ge=0, le=50)
    temp_high_c:                 float = Field(..., ge=50)
    max_temperature_c:           float = Field(..., ge=80)
    res_dc_ohm_per_m:            float = Field(..., gt=0)
    res_low_ohm_per_m:           float = Field(..., gt=0)
    res_high_ohm_per_m:          float = Field(..., gt=0)
    elastic_modulus_gpa:         float = Field(..., gt=0)
    coeff_thermal_expan_per_c:   float = Field(..., gt=0)
    cost_dol_per_km:             float = Field(0.0, ge=0)
    installation_dol_per_km:     float = Field(0.0, ge=0)
    accessories_dol_per_km:      float = Field(0.0, ge=0)
    str_costs_dol:               float = Field(0.0, ge=0)
    emissivity:                  float = Field(0.5, ge=0, le=1)
    solar_absorptivity:          float = Field(0.5, ge=0, le=1)

    def __add__(self, other):
        from refa import LineDesignMetric, Line
        if isinstance(other, LineDesignMetric):
            return Line(line_design=other.model_copy(deep=True), 
                        conductor=self.model_copy(deep=True))
        return NotImplemented

class ConductorImperial:
    """
    Not a Pydantic model — just a converter.
    Calling ConductorImperial(...) converts imperial inputs
    and returns a ConductorMetric instance directly.
    """
    def __new__(cls,
                type:                        str,
                code:                        str,
                area_kcmil:                  float = Field(..., gt=0),
                diameter_in:                 float = Field(..., gt=0),
                weight_lbs_per_kft:          float = Field(..., gt=0),
                conductor_rts_kip:           float = Field(..., gt=0),
                temp_dc_f:                   float = Field(..., ge=CF.c_to_f(0), le=CF.c_to_f(100)),
                temp_low_f:                  float = Field(..., ge=CF.c_to_f(0), le=CF.c_to_f(50)),
                temp_high_f:                 float = Field(..., ge=CF.c_to_f(50)),
                max_temperature_f:           float = Field(..., ge=CF.c_to_f(80)),
                res_dc_ohm_per_mile:         float = Field(..., gt=0),
                res_low_ohm_per_mile:        float = Field(..., gt=0),
                res_high_ohm_per_mile:       float = Field(..., gt=0),
                elastic_modulus_ksi:         float = Field(..., gt=0),
                coeff_thermal_expan_per_f:   float = Field(..., gt=0),
                cost_dol_per_kft:            float = Field(0.0, ge=0),
                installation_dol_per_kft:    float = Field(0.0, ge=0),
                accessories_dol_per_kft:     float = Field(0.0, ge=0),
                emissivity:                  float = 0.5,
                solar_absorptivity:          float = 0.5) -> ConductorMetric:
        """
        Returns a ConductorMetric directly.
        ConductorImperial is never instantiated.
        """
        return ConductorMetric(
            type                        = type,
            code                        = code,
            area_mm2                    = area_kcmil                 * CF.kcmil_to_mm2,
            diameter_mm                 = diameter_in                * CF.in_to_mm,
            weight_n_per_m              = weight_lbs_per_kft         * CF.lbs_per_kft_to_n_per_m,
            conductor_rts_kn            = conductor_rts_kip          * CF.kip_to_kn,
            temp_dc_c                   = CF.f_to_c(temp_dc_f),
            temp_low_c                  = CF.f_to_c(temp_low_f),
            temp_high_c                 = CF.f_to_c(temp_high_f),
            max_temperature_c           = CF.f_to_c(max_temperature_f),
            res_dc_ohm_per_m            = res_dc_ohm_per_mile        * CF.m_to_mile,
            res_low_ohm_per_m           = res_low_ohm_per_mile       * CF.m_to_mile,
            res_high_ohm_per_m          = res_high_ohm_per_mile      * CF.m_to_mile,
            elastic_modulus_gpa         = elastic_modulus_ksi        * CF.ksi_to_gpa,
            coeff_thermal_expan_per_c   = coeff_thermal_expan_per_f  * 9 / 5,
            cost_dol_per_km             = cost_dol_per_kft           * CF.m_to_ft,
            installation_dol_per_km     = installation_dol_per_kft   * CF.m_to_ft,
            accessories_dol_per_km      = accessories_dol_per_kft    * CF.m_to_ft,
            emissivity                  = emissivity,
            solar_absorptivity          = solar_absorptivity,
        )