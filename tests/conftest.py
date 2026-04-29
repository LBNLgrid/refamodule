import pytest
from refa import LineDesign, Conductor, Line
from refa.defaults import (
    default_economics,
    default_clear_environment,
    default_structure_config_ac,
    default_structure_config_dc,
    acsr_795_0_drake,
    acss_795_0_cuckoo,
    accc_1035_dublin,
)
from refa.standards import nesc_250b_heavy


@pytest.fixture
def environment():
    return default_clear_environment()


@pytest.fixture
def structure_config_ac():
    return default_structure_config_ac()


@pytest.fixture
def structure_config_dc():
    return default_structure_config_dc()


@pytest.fixture
def economics():
    return default_economics()


@pytest.fixture
def loading():
    return nesc_250b_heavy()


@pytest.fixture
def line_design1(environment):
    return LineDesign(
        environment=environment,
        nbr_circuits=1,
        nbr_bundles=3,
        nbr_conds_per_bundle=1,
        length_km=10,
        avg_span_m=250,
        max_span_m=300,
    )


@pytest.fixture
def line_design2(environment):
    return LineDesign(
        environment=environment,
        nbr_circuits=1,
        nbr_bundles=3,
        nbr_conds_per_bundle=1,
        length_km=30,
        avg_span_m=300,
        max_span_m=300,
    )


@pytest.fixture
def conductor_acss():
    return acss_795_0_cuckoo()


@pytest.fixture
def conductor_acsr():
    return acsr_795_0_drake()


@pytest.fixture
def conductor_accc():
    return accc_1035_dublin()


@pytest.fixture
def line1(line_design1, conductor_acss):
    """ACSS Cuckoo on 10 km line — primary test line matching notebook outputs."""
    return Line(line_design=line_design1, conductor=conductor_acss)


@pytest.fixture
def line2(line_design2, conductor_acsr):
    """ACSR Drake on 30 km line, built via + operator."""
    return line_design2 + conductor_acsr


@pytest.fixture
def line3(line_design1, conductor_accc):
    """ACCC Dublin on 10 km line, built via reversed + operator."""
    return conductor_accc + line_design1
