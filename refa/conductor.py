from pydantic import BaseModel, Field


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


    def __add__(self, other):
        from .line_design import LineDesign
        from .line import Line
        if isinstance(other, LineDesign):
            return Line(line_design=other.model_copy(deep=True), 
                        conductor=self.model_copy(deep=True))
        return NotImplemented