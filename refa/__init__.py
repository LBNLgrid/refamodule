from .conductor import ConductorMetric, ConductorImperial
from .environment import EnvironmentMetric, EnvironmentImperial
from .line_design import LineDesignMetric, LineDesignImperial
from .loading import LoadingMetric, LoadingImperial
from .structure_config import (
    StructureConfigACmetric, StructureConfigACimperial, StructureConfigDCmetric, StructureConfigDCimperial
)
from .line import Line
from .economics import Economics
from .project import Rebuild, Reconductoring, VoltageUpgrade, HVDC, Existing, Analysis

# from .parameter_access import UnitSystem
from .system_parameters import UnitSystem

if UnitSystem.is_imperial():
    Conductor = ConductorImperial
    Environment = EnvironmentImperial
    LineDesign = LineDesignImperial
    Loading = LoadingImperial
    StructureConfigAC = StructureConfigACimperial
    StructureConfigDC = StructureConfigDCimperial
else:
    Conductor = ConductorMetric
    Environment = EnvironmentMetric
    LineDesign = LineDesignMetric
    Loading = LoadingMetric
    StructureConfigAC = StructureConfigACmetric
    StructureConfigDC = StructureConfigDCmetric

