from ..economics import Economics

def default_economics() -> Economics:
    return Economics(
        conductors_lifetime=40,
        structures_lifetime=60,
        wacc=0.07,
        inflation=0.02,
        cost_of_losses_dol_per_mwh=40,
        cost_of_congestion_dol_per_mwh=1,
        cost_of_structures_dol_per_unit=100000
    )