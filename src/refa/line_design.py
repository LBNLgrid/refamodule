import math
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from .environment import Environment


class LineDesign(BaseModel):
    environment: Environment
    nbr_circuits: int = Field(..., ge=1, le=3)
    nbr_bundles: int = Field(..., ge=2, le=3) # number of phases in ac, number of poles in dc
    nbr_conds_per_bundle: int = Field(..., ge=1) # number of conductors per phase in ac, number of conductors per pole in dc
    length_km: float = Field(..., gt=0)
    avg_span_m: float = Field(..., gt=0)
    max_span_m: float = Field(..., gt=0)
    
    nbr_structures: Optional[int] = Field(default=None, ge=1)
    max_sag_m: float = None
    structore_cost_dol: float = Field(0, ge=0)
    
    @model_validator(mode="after")
    def _update_parameters(self):
        # ensure unique instances of objects
        self.environment = self.environment.model_copy(deep=True)
        # set nbr_structures
        if self.nbr_structures is None:
            self.nbr_structures = math.ceil(self.length_km * 1000 / self.avg_span_m) + 1
        return self

    def __getattr__(self, name):
        env = object.__getattribute__(self, "environment")
        if hasattr(env, name):
            return getattr(env, name)
        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

    def __add__(self, other):
        from .conductor import Conductor
        from .line import Line
        if isinstance(other, Conductor):
            return Line(line_design=self.model_copy(deep=True), 
                        conductor=other.model_copy(deep=True))
        return NotImplemented