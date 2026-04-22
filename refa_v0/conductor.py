from pydantic import BaseModel
from pydantic import BaseModel, Field, validator

class Conductor(BaseModel):
    """Conductor parameters."""
    type: str
    code: str
    area_mm2: float = Field(..., gt=0)
    diameter_mm: float = Field(..., gt=0)
    weight_n_per_m: float = Field(..., gt=0)
    conductor_rts_kn: float = Field(..., gt=0)
    dol_per_1000_ft: float = Field(..., ge=0)
    inst_dol_per_1000_ft: float = Field(..., ge=0)
    accessories_dol_per_1000_ft: float = Field(..., ge=0)
    str_costs_dol: float = Field(..., ge=0)
    temp_dc_c: float = Field(..., ge=0)
    temp_low_c: float = Field(..., ge=0)
    temp_high_c: float = Field(..., ge=0)
    max_temperature_c: float = Field(..., ge=0)
    res_dc_ohm_per_m: float = Field(..., ge=0)
    res_low_ohm_per_m: float = Field(..., ge=0)
    res_high_ohm_per_m: float = Field(..., ge=0)
    elastic_modulus_gpa: float = Field(..., gt=0)
    coeff_thermal_expan_per_cel: float = Field(..., gt=0)
    emissivity: float = Field(..., gt=0)
    solar_absorptivity: float = Field(..., gt=0)

    # Attributes that will be updated/used throughout the calculations
    losses_at_peak_mwh_per_m: float = 0
    congestion_mw: float = 0
    corona_losses_mwh_per_m: float = 0

    