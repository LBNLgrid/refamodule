from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, List, Dict


class Structure(BaseModel):
    """Sub‑model for defining structure specifications (used in AdvancedOptions and VoltageUpgrade)."""
    type: str
    height_m: float = Field(..., gt=0)
    material: str
    cost_dol: float = Field(..., ge=0)
    # … add any other fields you need …