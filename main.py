from refa import (
    LineDesign, Conductor, Line, Rebuild, Reconductoring, VoltageUpgrade, HVDC, Existing, Analysis
)
from refa.defaults import (
    default_economics,
    default_clear_environment, default_clear_environment_imperial,
    default_conductor, default_conductor_imperial,
    default_structure_config_ac, default_structure_config_ac_imperial,
    default_structure_config_dc, default_structure_config_dc_imperial
)
import datetime

# my_conductor = default_conductor()
# my_environment = default_clear_environment()
# my_structure_config_ac = default_structure_config_ac()
# my_structure_config_dc = default_structure_config_dc()

my_conductor = default_conductor_imperial()
my_environment = default_clear_environment_imperial()
my_structure_config_ac = default_structure_config_ac_imperial()
print(my_structure_config_ac)
my_structure_config_dc = default_structure_config_dc_imperial()

my_economics = default_economics()

from refa.standards import nesc_250b_heavy, nesc_250b_heavy_imperial

# my_loading = nesc_250b_heavy()
# print(my_loading)

my_loading = nesc_250b_heavy_imperial()
print(my_loading.get_parameter_info('pressure'))
print(my_loading.get_parameter('wind_ice_temperature'))

# imperial
from refa.defaults import default_conductor_imperial, acsr_795_0_drake, acss_795_0_cuckoo, accc_1035_dublin
from refa.system_parameters import CF

line_design1 = LineDesign(
    environment=my_environment,
    nbr_circuits=1,
    nbr_bundles=3,
    nbr_conds_per_bundle=1,
    length_mile=10,
    avg_span_ft=250,
    max_span_ft=300
)
line_design2 = LineDesign(
    environment=my_environment,
    nbr_circuits=1,
    nbr_bundles=3,
    nbr_conds_per_bundle=1,
    length_mile=30,
    avg_span_ft=300,
    max_span_ft=300
)
print("Line design -> ", line_design1)

conductor = Conductor(
        type='ACSR',
        code='266.8_PARTRIDGE',
        area_kcmil=157.0 * CF.mm2_to_kcmil,
        diameter_in=16.0 * CF.mm_to_in,
        weight_lbs_per_kft=5.36 * CF.n_per_m_to_lbs_per_kft,
        conductor_rts_kip=50.26 * CF.kn_to_kip,
        cost_dol_per_kft=735.0 * CF.ft_to_m,
        installation_dol_per_kft=1027.0 * CF.ft_to_m,
        accessories_dol_per_kft=263.0 * CF.ft_to_m,
        temp_dc_f=CF.c_to_f(40),
        temp_low_f=CF.c_to_f(45),
        temp_high_f=CF.c_to_f(160),
        max_temperature_f=CF.c_to_f(180),
        res_dc_ohm_per_mile=0.000209 * CF.mile_to_m,
        res_low_ohm_per_mile=0.000209 * CF.mile_to_m,
        res_high_ohm_per_mile=0.000256 * CF.mile_to_m,
        elastic_modulus_ksi=75.5 * CF.gpa_to_ksi,
        coeff_thermal_expan_per_f=1.92e-05 * 5 / 9,
        emissivity=0.5,
        solar_absorptivity=0.5
)
print("Conductor using constructor -> ", conductor)

conductor1 = default_conductor_imperial()
print("Conductor from default database -> ", conductor1)

conductor2 = acsr_795_0_drake()
conductor3 = accc_1035_dublin()

line1 = Line(line_design=line_design1, conductor=conductor1)
line2 = line_design2 + conductor2
line3 = conductor3 + line_design1

print(line1)


temperature_from_current = line1.temperature_at_current(current_a=1400) 
resistance_from_current = line1.resistance_at_current(current_a=1400)
temperature_from_p_and_v = line1.temperature_at_current(power_mw=550, voltage_kv=345)
resistance_from_p_and_v = line1.resistance_at_current(power_mw=550, voltage_kv=345)
print(f"Conductor temperature when current is provided -> {temperature_from_current}")
print(f"Conductor resistance when current is provided -> {resistance_from_current}")
print(f"Conductor temperature when power and voltage are provided -> {temperature_from_p_and_v}")
print(f"Conductor resistance when power and voltage are provided -> {resistance_from_p_and_v}")

ampacity = line1.ampacity_at_environment()
print(f"Ampacity -> {ampacity}")

sag_from_peak_current = line1.sag_at_current(current_a=1400, initial_tension_percentage=0.2)
sag_from_power_and_voltage = line1.sag_at_power_and_voltage(power_mw=500, voltage_kv=230, initial_tension_percentage=0.2)
sag_from_conductor_temperature = line1.sag_at_temperature(temp_at_current_f=185, initial_tension_percentage=0.2)
sag_from_loading_profile = line1.sag_at_loading(loading_conditions=my_loading, initial_tension_percentage=0.2)
print(f"Sag when peak current is provided -> {sag_from_peak_current}")
print(f"Sag when conductor temperature is provided -> {sag_from_conductor_temperature}")
print(f"Sag when a wind/ice loading profile is provided -> {sag_from_loading_profile}")

corona_inception_voltage = line1.corona_inception_voltage(structure_config=my_structure_config_ac) 
corona_voltage_gradient = line1.corona_voltage_gradient(structure_config=my_structure_config_ac)
print(f"Corona Inception voltage -> {corona_inception_voltage}")
print(f"Corona voltage gradient -> {corona_voltage_gradient}")


resistive_line_losses_from_current = line1.resistive_line_losses(current_a=1400, load_factor=0.6)
resistive_line_losses_with_congestion = \
    line1.resistive_line_losses_considering_congestion(power_mw=550, voltage_kv=230, load_factor=0.6)
print(f"Resistive line losses when current is provided -> {resistive_line_losses_from_current}")
print(f"Resistive line losses when power is provided -> {resistive_line_losses_with_congestion}")

corona_discharge_losses = line1.corona_discharge_losses(
    voltage_kv=230, load_factor=0.6, structure_config=my_structure_config_ac
)
print(f"Corona discharge losses -> {corona_discharge_losses}")

corona_discharge_losses_dc = line1.corona_discharge_losses(
    voltage_kv=230, load_factor=0.6, structure_config=my_structure_config_dc, is_hvdc=True
)
print(f"Corona discharge losses (DC line) -> {corona_discharge_losses_dc}")

congestion_from_current = line1.congestion(current_a=1500, voltage_kv=230)
congestion_from_power = line1.congestion(power_mw=700, voltage_kv=230)
print(f"Congestion when current is provided -> {congestion_from_current}")
print(f"Congestion when power is provided -> {congestion_from_power}")


technical_perf_from_current = line1.overall_technical_performance(current_a=1500)
print(f"Overall performance when only current is provided -> {technical_perf_from_current}")

technical_perf_from_power_and_voltage = line1.overall_technical_performance(
    power_mw=500, voltage_kv=230
)
print(f"Overall performance when power and voltage are provided -> {technical_perf_from_power_and_voltage}")

technical_perf_including_losses = line1.overall_technical_performance(
    current_a=1500, load_factor=0.6
)
print(f"Overall performance including losses -> {technical_perf_including_losses}")

technical_perf_including_losses_and_corona = line1.overall_technical_performance(
    current_a=1500, voltage_kv=230, load_factor=0.6, structure_config=my_structure_config_ac
)
print(f"Overall performance including corona discharge -> {technical_perf_including_losses_and_corona}")


# line1.is_ampacity_feasible(current_a=1172)
# line1.is_ampacity_feasible(power_mw=700, voltage_kv=345) 

print("Line sag feasibility -> ", 
    line1.is_sag_feasible(current_a=1300, max_sag_ft=10, initial_tension_percentage=0.3))

print("Line corona feasibility -> ",
    line1.is_corona_feasible(structure_config=my_structure_config_ac, voltage_kv=345))


rebuild_prj = Rebuild(
    conductor_list=[acsr_795_0_drake(), acss_795_0_cuckoo(), accc_1035_dublin()], 
    line_design=line_design2,
    economics=my_economics,
    power_mw=400,
    voltage_kv=230,
    structure_config=my_structure_config_ac,
    select_ampacity_feasible=False,
    select_sag_feasible=False,
    select_corona_feasible=False
)
reconductoring_prj = Reconductoring(
    line_list=[line1, line2], 
    economics=my_economics,
    power_mw=400,
    voltage_kv=230,
    structure_remaining_life=25
)
voltageupgrade_prj = VoltageUpgrade(
    line_list=[line2, line1], 
    economics=my_economics,
    power_mw=400,
    voltage_kv=345, 
    structure_remaining_life=0, 
    conductor_remaining_life=0,
    cost_substations_upgrade_dol=2000000  
)
hvdc_prj = HVDC(
    line_list=[line3, line2], 
    economics=my_economics,
    power_mw=400,
    voltage_kv=500, 
    structure_remaining_life=0, 
    conductor_remaining_life=0, 
    cost_converters_dol=3000000,
    nbr_dc_poles_per_circuit=2,
    structure_config=my_structure_config_dc
)
existing_project = Existing(
    line_list=[line1], 
    economics=my_economics,
    power_mw=400,
    voltage_kv=230,
    structure_remaining_life=25,
    conductor_remaining_life=15
)


print(rebuild_prj.total_costs(time_horizon=65))
# rebuild_prj.total_costs(time_horizon=65, report_all_years=True)
# rebuild_prj.total_costs_including_losses(time_horizon=65, load_factor=0.6)
# rebuild_prj.structure_costs(time_horizon=65)
# rebuild_prj.conductor_costs(time_horizon=65)
# rebuild_prj.losses_costs(time_horizon=65, load_factor=0.6)

# reconductoring_prj.total_costs(time_horizon=65)
# reconductoring_prj.total_costs_including_losses(time_horizon=65, load_factor=0.6)
# reconductoring_prj.structure_costs(time_horizon=65)
# reconductoring_prj.conductor_costs(time_horizon=65)
# reconductoring_prj.losses_costs(time_horizon=65, load_factor=0.6)
# reconductoring_prj.congestion_costs(time_horizon=65)

# voltageupgrade_prj.total_costs(time_horizon=70)
# hvdc_prj.total_costs(time_horizon=70)


refa = Analysis(project_list=[
    rebuild_prj, reconductoring_prj, voltageupgrade_prj, hvdc_prj, existing_project
    ])
print(refa.total_costs_of_projects(time_horizon=70))
# refa.total_costs_of_projects_including_losses(time_horizon=70, load_factor=0.6)

# refa.structure_costs_of_projects(time_horizon=70)
# refa.conductor_costs_of_projects(time_horizon=70, select_feasible=False)
# refa.losses_costs_of_projects(time_horizon=70, load_factor=0.6)
# refa.congestion_costs_of_projects(time_horizon=70)

print(f"line design imperial: {line_design1}")