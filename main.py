from refa import (
    LineDesign, Line, Rebuild, Reconductoring, VoltageUpgrade, HVDC, Existing, Analysis
)
from refa.defaults import (
    default_economics,
    default_clear_environment,
    default_conductor,
    acsr_795_0_drake,
    acss_795_0_cuckoo,
    default_structure_config_ac,
    default_structure_config_dc
)
from refa.standards import nesc_250b_heavy

my_conductor = default_conductor()
my_environment = default_clear_environment()
my_structure_config_ac = default_structure_config_ac()
my_structure_config_dc = default_structure_config_dc()

my_corridor = LineDesign(
    environment=my_environment,
    nbr_circuits=1,
    nbr_bundles=3,
    nbr_conds_per_bundle=1,
    length_km=10,
    avg_span_m=250,
    max_span_m=300
)

cond1 = acss_795_0_cuckoo()
cond2 = acsr_795_0_drake()

my_economics = default_economics()

ln1 = Line(line_design=my_corridor, conductor=acss_795_0_cuckoo())
ln2 = my_corridor + acsr_795_0_drake()

prj0 = Existing(
    line_list=[ln1], 
    economics=my_economics,
    power_mw=400,
    voltage_kv=230,
    structure_remaining_life=25,
    conductor_remaining_life=15
)
prj1 = Rebuild(
    line_list=[ln1, ln2], 
    economics=my_economics,
    power_mw=400,
    voltage_kv=230,
    structure_config=my_structure_config_ac
)
prj2 = Reconductoring(
    conductor_list=[acsr_795_0_drake(), acss_795_0_cuckoo()], 
    line_design=my_corridor,
    economics=my_economics, 
    power_mw=400,
    voltage_kv=230,
    structure_remaining_life=15
)
prj3 = VoltageUpgrade(
    line_list=[ln1, ln2], 
    economics=my_economics,
    power_mw=400,
    voltage_kv=345, 
    structure_remaining_life=0, 
    conductor_remaining_life=0, 
)
prj4 = HVDC(
    line_list=[ln1, ln2], 
    economics=my_economics,
    power_mw=400,
    voltage_kv=500, 
    structure_remaining_life=0, 
    conductor_remaining_life=0, 
    nbr_dc_poles_per_circuit=2,
    structure_config=my_structure_config_dc
)

print(prj1.calculate_total_npv(70))

refa = Analysis(project_list=[prj1, prj2, prj3, prj4, prj0])
comparison = refa.compare_project_total_costs(time_horizon=70, load_factor=0.6)

print(comparison)
