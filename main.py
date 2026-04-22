from refa import (
    LineDesign, Line, Project, Rebuild, Reconductoring, VoltageUpgrade, HVDC, Existing, Analysis
)
from refa.defaults import (
    default_economics,
    default_clear_environment,
    default_conductor,
    acsr_795_0_drake,
    acss_795_0_cuckoo,
    default_structure_config_ac,
)
from refa.standards import nesc_250b_heavy

my_conductor = default_conductor()
my_environment = default_clear_environment()
my_structure = default_structure_config_ac()

my_corridor = LineDesign(
    environment=my_environment,
    voltage_kv=230,
    nbr_circuits=1,
    nbr_bundles=3,
    nbr_conds_per_bundle=1,
    length_km=10,
    avg_span_m=250,
    span_m=300
)

# loading = nesc_250b_heavy()
# my_line = my_corridor + my_conductor
# amp = my_line._ieee_738_steady_state_rating()
# sag = my_line.calculate_sag(loading_conditions=loading, current_a=1500,
#                             initial_tension_percentage=0.5)

cond1 = acss_795_0_cuckoo()
cond2 = acsr_795_0_drake()

my_economics = default_economics()
# my_project = Rebuild.from_single_line_design(
#     conductor_list=[cond1, cond2], 
#     line_design=my_corridor, 
#     economics=my_economics,
#     power_mw=400,
#     replace_st_at=0,
#     replace_cd_at=0
# )

ln1 = Line(line_design=my_corridor, conductor=acss_795_0_cuckoo())
ln2 = my_corridor + acsr_795_0_drake()

prj1 = Rebuild(
    line_list=[ln1, ln2], 
    economics=my_economics,
    power_mw=400,
    replace_st_at=0,
    replace_cd_at=0
)
prj2 = Reconductoring(
    line_list=[ln1, ln2], 
    economics=my_economics,
    power_mw=400,
    replace_st_at=20,
    replace_cd_at=0
)
prj3 = VoltageUpgrade(
    line_list=[ln1, ln2], 
    economics=my_economics,
    power_mw=400,
    replace_st_at=15,
    replace_cd_at=0, voltage_new_kv=345
)
prj4 = HVDC(
    line_list=[ln1, ln2], 
    economics=my_economics,
    power_mw=400,
    replace_st_at=0,
    replace_cd_at=0, voltage_new_kv=400, nbr_dc_poles=2, distance_pos_neg_poles_m=8
)

print(prj1.calculate_total_npv(70))

refa = Analysis(list_of_projects=[prj1, prj2, prj3, prj4])
comparison = refa.compare_project_total_costs(time_horizon=70, load_factor=0.6)

print(comparison)
