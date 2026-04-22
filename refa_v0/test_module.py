"""
Testing the refa module with sample data and configurations.
"""
from pathlib import Path
import json
from project import Project, Existing, Rebuild, Reconductoring, VoltageUpgrade, HVDC
from line import Line 
from conductor import Conductor
import pandas as pd

# print("Model fields →", list(Line.__fields__.keys()))
# path = Path('input_data_raw/parameter_cfg.json')
# raw = json.loads(path.read_text())
# print(json.dumps(raw, indent=2))
with open('input_data_raw/parameter_cfg.json', 'r') as f:
    nested_dict = json.load(f)
flat = pd.json_normalize(nested_dict, sep='.')
flat.columns = [col.split('.')[-1] for col in flat.columns]
flat_dict = flat.to_dict(orient='records')[0]

# print("Flat dict →", json.dumps(flat_dict, indent=2))

line_obj = Line(**flat_dict)
# print("Line object →", line_obj)
cond_raw = {
        "type": "AA",
        "code": "CU1/0",
        "area_mm2": 450.0,
        "diameter_mm": 29.0,
        "weight_n_per_m": 17,
        "conductor_rts_kn": 135,
        "dol_per_1000_ft": 800,
        "inst_dol_per_1000_ft": 1200,
        "accessories_dol_per_1000_ft": 0,
        "str_costs_dol": 0,
        "temp_dc_c": 20,
        "temp_low_c": 25,
        "temp_high_c": 75,
        "max_temperature_c": 100,
        "res_low_ohm_per_m": 7.02e-5,
        "res_high_ohm_per_m": 8.63e-5,
        "res_dc_ohm_per_m": 7.02e-5,
        "elastic_modulus_gpa": 75,
        "coeff_thermal_expan_per_cel": 1.22e-5,
        "emissivity": 0.5,
        "solar_absorptivity": 0.5
    }
line_obj.conductors_list = [Conductor(**cond_raw)]

# --- Testing of Line obj

# print("Line object with conductor →", line_obj)

res = line_obj.calculate_ampacity(current_a=1500, only_feasible_conds=False)
print("Ampacity calculation result → \n", res[['type', 'code', 'env_ampacity_a']])

# res_temp = line_obj.calculate_temperature_and_resistance_at_current(current_a=1500)
# print("Temperature and resistance calculation result →", res_temp[['type', 'code', 'temp_at_current_c', 'res_at_current_ohm_per_m']])

res_losses = line_obj.calculate_resistive_line_losses(current_a=1500, load_factor=0.8)
print("Resistive line losses calculation result → \n", res_losses[['type', 'code', 'losses_at_peak_mwh_per_m']])

res_cong = line_obj.calculate_congestion(current_a=1500)
print("Congestion calculation result → \n", res_cong[['type', 'code', 'congestion_mw']])

res_sag = line_obj.calculate_sag(current_a=1500)
print("Sag calculation result → \n", res_sag[['type', 'code', 'sag_m', 'tension_n']])

# --- Testing of Project object
prj_obj = Rebuild(**flat_dict)
cond_df = pd.DataFrame([cond_raw])
cond_df = pd.merge(cond_df, res_losses)
cond_dict = cond_df.to_dict(orient='records')[0]
print("Updated Conductor --> \n", cond_dict)
prj_obj.conductors_list = [Conductor(**cond_dict)]

npv = prj_obj.calculate_total_npv(70)
print("Total NPV --> \n", npv)
st = prj_obj.calculate_structure_costs(70)
print("Structure Cost --> \n", st)
# ss = prj_obj.calculate_converter_costs(70)
# print("SS + Transfo Costs --> \n", ss)
ls = prj_obj.calculate_losses_costs(70)
print("Losses Cost --> \n", ls)

res_cg = prj_obj.calculate_congestion(2708)
cond_df = pd.DataFrame([cond_raw])
cond_df = pd.merge(cond_df, res_cg)
cond_dict = cond_df.to_dict(orient='records')[0]
print("Updated Conductor --> \n", cond_dict)
prj_obj.conductors_list = [Conductor(**cond_dict)]
cg = prj_obj.calculate_congestion_costs(70)
print("Congestion cost --> \n", cg)

techn_perf = prj_obj.calculate_overall_technical_performance(current_a=1000)
print("Technical Performance --> \n", techn_perf)


# --- Testing of REFA object
from refa import REFA

prj_obj2 = Project(**prj_obj.model_dump())
prj_obj2.prj_name = "New Line"

refa_obj = REFA(time_horizon=70)
res_cmpr_prj = refa_obj.compare_projects([prj_obj, prj_obj2])
print("Project Comparison Result: \n", res_cmpr_prj)