import math
from pydantic import BaseModel, Field, model_validator
from .environment import EnvironmentMetric
from .system_parameters import ParameterAccess, CF


class LineDesignMetric(BaseModel, ParameterAccess):
    environment:          EnvironmentMetric
    nbr_circuits:         int            = Field(..., ge=1, le=3)
    nbr_bundles:          int            = Field(..., ge=2, le=3) # number of phases in ac, number of poles in dc
    nbr_conds_per_bundle: int            = Field(..., ge=1) # number of conductors per phase in ac, number of conductors per pole in dc
    length_km:            float          = Field(..., gt=0)           
    avg_span_m:           float          = Field(..., gt=0)           
    max_span_m:           float          = Field(..., gt=0)         
    
    nbr_structures:       int | None     = Field(None, gt=0)
    max_sag_m:            float | None   = Field(None, gt=0)
    structore_cost_dol:   float          = Field(0, ge=0)

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
        from refa import ConductorMetric, Line
        if isinstance(other, ConductorMetric):
            return Line(line_design=self.model_copy(deep=True), 
                        conductor=other.model_copy(deep=True))
        return NotImplemented
    
class LineDesignImperial:
    def __new__(cls,
                environment:          EnvironmentMetric,
                nbr_circuits:         int,
                nbr_bundles:          int,
                nbr_conds_per_bundle: int,
                length_mile:          float,
                avg_span_ft:          float,
                max_span_ft:          float,
                nbr_structures:       int   = None,
                max_sag_ft:           float = None,
                structore_cost_dol:   float = 0) -> LineDesignMetric:
        return LineDesignMetric(
            environment          = environment,
            nbr_circuits         = nbr_circuits,
            nbr_bundles          = nbr_bundles,
            nbr_conds_per_bundle = nbr_conds_per_bundle,
            length_km            = length_mile        * CF.mile_to_km,
            avg_span_m           = avg_span_ft        * CF.ft_to_m,
            max_span_m           = max_span_ft        * CF.ft_to_m,
            nbr_structures       = nbr_structures,
            max_sag_m            = max_sag_ft * CF.ft_to_m if max_sag_ft is not None else None,
            structore_cost_dol   = structore_cost_dol,
        )