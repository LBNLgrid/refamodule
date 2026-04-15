from refa import LineStructure
from refa.defaults import default_conductor,default_clear_environment
from refa.standards import nesc_250b_heavy

my_conductor = default_conductor()
my_environment = default_clear_environment()

my_corridor = LineStructure(
    environment=my_environment,
    nbr_circuits=1,
    length_km=10,
    avg_span_m=250,
    span_m=300,
    max_sag_m=12,
)

loading = nesc_250b_heavy()
my_line = my_corridor + my_conductor
amp = my_line._ieee_738_steady_state_rating()
sag = my_line.calculate_sag(loading_conditions=loading, current_a=1500,
                            initial_tension_percentage=0.5)

my_line.is_feasible(ampacity= , sag=)

print(amp)
print(sag)