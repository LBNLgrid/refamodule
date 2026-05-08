from ..structure_config import (
    StructureConfigACmetric, StructureConfigDCmetric, 
    StructureConfigACimperial, StructureConfigDCimperial
)


def default_structure_config_ac():
    return StructureConfigACmetric(
        distance_a_b_m=4, 
        distance_a_c_m=4,
        distance_b_c_m=4,
        structure_height_m=25.0
    )


def default_structure_config_dc():
    return StructureConfigDCmetric(
        distance_pos_neg_poles_m=4,
        structure_height_m=25.0
    )


def default_structure_config_ac_imperial():
    return StructureConfigACimperial(
        distance_a_b_ft=12, 
        distance_a_c_ft=12,
        distance_b_c_ft=12,
        structure_height_ft=75.0
    )


def default_structure_config_dc_imperial():
    return StructureConfigDCimperial(
        distance_pos_neg_poles_ft=12,
        structure_height_ft=75.0
    )