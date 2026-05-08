from pydantic import BaseModel, Field
from .system_parameters import ParameterAccess, CF


class StructureConfigACmetric(BaseModel, ParameterAccess):
    structure_height_m: float = Field(..., gt=0, description="Height of a representative structure (m). Used in Corona calculations.")
    distance_a_b_m: float = Field(..., gt=0, description="Distance between phase A and B (m)")
    distance_a_c_m: float = Field(..., gt=0, description="Distance between phase A and C (m)")
    distance_b_c_m: float = Field(..., gt=0, description="Distance between phase B and C (m)")


class StructureConfigACimperial:
    def __new__(cls,
                structure_height_ft: float = Field(..., gt=0),
                distance_a_b_ft: float = Field(..., gt=0),
                distance_a_c_ft: float = Field(..., gt=0),
                distance_b_c_ft: float = Field(..., gt=0)) -> StructureConfigACmetric:
        
        return StructureConfigACmetric(
            structure_height_m=structure_height_ft * CF.ft_to_m,
            distance_a_b_m=distance_a_b_ft * CF.ft_to_m,
            distance_a_c_m=distance_a_c_ft * CF.ft_to_m,
            distance_b_c_m=distance_b_c_ft * CF.ft_to_m,
        )


class StructureConfigDCmetric(BaseModel, ParameterAccess):
    structure_height_m: float = Field(..., gt=0, description="Height of a representative structure (m). Used in Corona calculations.")
    distance_pos_neg_poles_m: float = Field(..., gt=0, description="Distance between positive and negative poles (m).")


class StructureConfigDCimperial:
    def __new__(cls,
                structure_height_ft: float = Field(..., gt=0),
                distance_pos_neg_poles_ft: float = Field(..., gt=0)) -> StructureConfigDCmetric:
        
        return StructureConfigDCmetric(
            structure_height_m=structure_height_ft * CF.ft_to_m,
            distance_pos_neg_poles_m=distance_pos_neg_poles_ft * CF.ft_to_m,
        )
