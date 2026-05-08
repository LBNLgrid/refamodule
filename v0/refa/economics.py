from pydantic import BaseModel, Field, model_validator

class Economics(BaseModel):
    """Economics‑tab – financial assumptions."""
    conductors_lifetime: int
    structures_lifetime: int
    wacc: float = Field(..., ge=0, le=1, description="Cost of capital (fraction)")
    inflation: float = Field(..., ge=0, le=1)
    cost_of_losses_dol_per_mwh: float = Field(..., ge=0, description="Cost of energy per MWh (dollars)")
    cost_of_congestion_dol_per_mwh: float = Field(..., ge=0, description="Congestion cost per MW (dollars)")
    cost_of_structures_dol_per_unit: float = Field(..., ge=0, description="Cost per structure (dollars)")

    @model_validator(mode="after")
    def _update_parameters(self):
        if self.cost_of_congestion_dol_per_mwh > self.cost_of_losses_dol_per_mwh:
            raise ValueError("Cost of congestion must be smaller than the cost of energy.")
