"""
Testing the refa module with sample data and configurations.
"""

import refa

refa_obj = refa.refa_basic(power_mw=400, 
                           length_km=20, 
                           avg_span_m=300, 
                           cost_of_structures_unit=70000, 
                           latitude=32, 
                           elevation_m=600.0, 
                           time_horizon=90, 
                           unit_system="Imperial")

# ---------------- Compare project options ----------------

# Create ProjectOption instances
prj_option1 = refa_obj.create_project_option({
    "option": "option1",
    "replace_st_at": 25,
    "replace_cd_at": 35,
    "voltage_kv": 230,
    "voltage_upgrade": False,
    "hvdc": False,
    "nbr_phases": 3
})

prj_option2 = refa_obj.create_project_option({
    "option": "option2",
    "replace_st_at": 30,
    "replace_cd_at": 40,
    "voltage_kv": 345,
    "voltage_upgrade": False,
    "hvdc": False,
    "nbr_phases": 3
})

res = refa_obj.compare_prj_options(prj_options=[prj_option1, prj_option2])

print("********************* Project Options Comparison:")
print(res['option1']['total_prj_perf'][0:3])

# ---------------- Keep Existing Line ----------------

# res1 = refa_obj.keep_existing_line()

# print("********************* Keeping Existing Line Performance:")
# print(res1['existing']['total_prj_perf'])


# ---------------- Compare Conductors ----------------    

# 1. Create a list of ConductorSpec instances (replace with your actual data)
cond1 = refa_obj.create_conductor_spec({
        "type": "AA",
        "code": "CU1/0",
        "area_mm2": 450.0,
        "diameter_mm": 29.0,
        "weight_n_per_m": 17,
        "conductor_rts_kn": 135,
        "dol_per_1000_ft": 800,
        "inst_dol_per_1000_ft": 1200,
        "accessories_dol_per_1000_ft": 0,
        "elastic_modulus_gpa": 75,
        "coeff_thermal_expan_per_cel": 1.22e-5,
        "emissivity": 0.5,
        "solar_absorptivity": 0.5
    })

cond2 = refa_obj.create_conductor_spec({
        "type": "AA",
        "code": "CU2/0",
        "area_mm2": 470.0,
        "diameter_mm": 30.0,
        "weight_n_per_m": 18,
        "conductor_rts_kn": 120,
        "dol_per_1000_ft": 1000,
        "inst_dol_per_1000_ft": 1500,
        "accessories_dol_per_1000_ft": 0,
        "elastic_modulus_gpa": 70,
        "coeff_thermal_expan_per_cel": 1.2e-5,
        "emissivity": 0.8,
        "solar_absorptivity": 0.9
    })
    # … add more ConductorSpec objects as needed …

res3 = refa_obj.compare_conductor_performance(conductors=[cond1, cond2], prj_option=prj_option1)
refa_obj.save_results(res3, "conductor_comparison")

# print("********************* Conductor Performance Comparison:")
# print(res3)


# # ---------------- Update configurations ----------------
# cfg = refa_obj.create_full_data_config({
#     "project": {"power_mw": 400, "voltage_kv": 115, "length_km": 50, "avg_span_m": 400, "span_m": 450},
#     "economics": {"wacc": 0.8}
# })

# print("********************* Updated Configuration:")
# print(cfg)