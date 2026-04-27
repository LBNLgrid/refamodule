from pydantic import BaseModel, Field

class Economics(BaseModel):
    """Economics‑tab – financial assumptions."""
    conductors_lifetime: int
    structures_lifetime: int
    wacc: float = Field(..., ge=0, le=1, description="Cost of capital (fraction)")
    inflation: float = Field(..., ge=0, le=1)
    cost_of_losses_dol_per_mwh: float = Field(..., ge=0, description="Cost of losses per MWh (dollars)")
    cost_of_congestion_dol_per_mwh: float = Field(..., ge=0, description="Congestion cost per MW (dollars)")
    cost_of_structures_dol_per_unit: float = Field(..., ge=0, description="Cost per structure (dollars)")
    
    tgt_structure_cost_dol: float = Field(0, ge=0, description="Cost of tangent structure in dollars.")
    ra_structure_cost_dol: float = Field(0, ge=0, description="Cost of running angle structure in dollars.")
    nade_structure_cost_dol: float = Field(0, ge=0, description="Cost of non-angled deadend structure in dollars.")
    de_structure_cost_dol: float = Field(0, ge=0, description="Cost of deadend structure in dollars.")