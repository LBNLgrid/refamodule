import math
from pydantic import BaseModel, Field, model_validator
from .environment import Environment


class LineStructure(BaseModel):
    environment: Environment
    nbr_circuits: int = Field(..., ge=1, le=3)
    length_km: float = Field(..., gt=0)
    avg_span_m: float = Field(..., gt=0)
    span_m: float = Field(..., gt=0)
    max_sag_m: float = Field(..., gt=0)
    nbr_structures: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def set_nbr_structures(self):
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
            return Line(structure=self, conductor=other)
        return NotImplemented