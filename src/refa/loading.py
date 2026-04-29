from pydantic import BaseModel, Field
from typing import Optional

class Loading(BaseModel):
    """Loading‑tab – mechanical loading profile."""
    wind_ice_temperature_c: float = Field(..., ge=-60, le=60)
    pressure_pa: float = 0
    ice_thickness_m: float = 0
    ice_density_kg_per_m3: float = 0
    additive_loading_n_per_m: float = 0

    