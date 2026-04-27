from ..structure_config import StructureConfigAC, StructureConfigDC

def default_structure_config_ac() -> StructureConfigAC:
    return StructureConfigAC(
        distance_a_b_m=4, 
        distance_a_c_m=4,
        distance_b_c_m=4,
        structure_height_m=25.0,
        nbr_tgt_structures=0,
        nbr_ra_structures=0,
        nbr_nade_structures=0,
        nbr_de_structures=0
    )


def default_structure_config_dc() -> StructureConfigDC:
    return StructureConfigDC(
        distance_pos_neg_poles_m=4,
        structure_height_m=25.0,
        nbr_tgt_structures=0,
        nbr_ra_structures=0,
        nbr_nade_structures=0,
        nbr_de_structures=0
    )