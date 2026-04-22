from pydantic import BaseModel, Field

class StructureConfig(BaseModel):
    structure_height_m: float = Field(..., gt=0, description="Used in Corona calculations. Height of a representative structure in meters.")
    
    # consider moving these two parameters to environment or conductor
    weather_correction_factor: float = Field(1.0, gt=0, description="Considered as 0.8 for rainy conditions.")
    rugosity_coefficient: float = Field(0.82, gt=0, description="1 for polished conductors, 0.92-0.98 for dirty conductors, and 0.8-0.87 for stranded conductors.")
    
    nbr_tgt_structures: int = Field(0, ge=0, description="Number of tangent structures in the line.")
    nbr_ra_structures: int = Field(0, ge=0, description="Number of running angle structures in the line.")
    nbr_nade_structures: int = Field(0, ge=0, description="Number of non-angled deadend structures in the line.")
    nbr_de_structures: int = Field(0, ge=0, description="Number of deadend structures in the line.")


class StructureConfigAC(StructureConfig):
    distance_a_b_m: float = Field(..., gt=0)
    distance_a_c_m: float = Field(..., gt=0)
    distance_b_c_m: float = Field(..., gt=0)
    

class StructureConfigDC(StructureConfig):
    distance_pos_neg_poles_m: float = Field(..., gt=0, description="Distance between positive and negative poles in case of HVDC (m)")
    