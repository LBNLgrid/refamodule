from pydantic import BaseModel, Field

class StructureConfig(BaseModel):
    structure_height_m: float = Field(..., gt=0, description="Used in Corona calculations. Height of a representative structure in meters.")
    
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
    