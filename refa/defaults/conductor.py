from ..conductor import Conductor

def default_conductor() -> Conductor:
    return Conductor(
        type="AA",
        code="CU1/0",
        area_mm2=450.0,
        diameter_mm=29.0,
        weight_n_per_m=17,
        conductor_rts_kn=135,
        dol_per_1000_ft=800,
        inst_dol_per_1000_ft=1200,
        accessories_dol_per_1000_ft=0,
        str_costs_dol=0,
        temp_dc_c=20,
        temp_low_c=25,
        temp_high_c=75,
        max_temperature_c=100,
        res_dc_ohm_per_m=7.02e-5,
        res_low_ohm_per_m=7.02e-5,
        res_high_ohm_per_m=8.63e-5,
        elastic_modulus_gpa=75,
        coeff_thermal_expan_per_cel=1.22e-5,
        emissivity=0.5,
        solar_absorptivity=0.5,
    )