import pytest

from ..loop_component import LoopVariable, LoopComponent

class Mock:
    def __init__(self, int_var=0, str_var='string', float_var = 0.0):
        self.int_var = int_var
        self.str_var = str_var
        self.float_var = float_var


@pytest.fixture
def mock():
    m = Mock()
    return m

@pytest.fixture
def simple_loop(mock):
    var = LoopVariable('int',mock.int_var, start=1, stop=9, step=2)
    print(var.values)
    loop = LoopComponent(parent=None, vars=var)
    return loop


def test_simple_loop(simple_loop):
    assert len(simple_loop) == 5


