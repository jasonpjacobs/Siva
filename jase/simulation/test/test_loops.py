import pytest

import numpy as np
from ..loop_component import LoopVariable, LoopComponent

class Mock:
    def __init__(self, int_var=0, str_var='string', float_var = 0.0):
        self.int_var = int_var
        self.str_var = str_var
        self.float_var = float_var


@pytest.fixture
def mock():
    global m
    m = Mock()
    return m

@pytest.fixture
def simple_loop(mock):
    var = LoopVariable('int',mock.int_var, start=1, stop=9, step=2)
    print(var.values)
    loop = LoopComponent(parent=None, vars=var)
    return loop



def test_loop_creation(mock):
    var = LoopVariable('int',mock.int_var, start=1, stop=9, step=2)
    assert len(var) == 5
    assert (var.values == np.array([1, 3, 5, 7, 9])).all()

    i=0
    for _ in var:
        assert mock.int_var == var.values[i]
        i+=1


    var = LoopVariable('int',mock.int_var, start=1, stop=10, step=2)
    assert len(var) == 5
    assert (var.values == np.array([1, 3, 5, 7, 9])).all()

    var = LoopVariable('int',mock.int_var, start=9, stop=1, step=-2)
    assert len(var) == 5
    assert (var.values == np.array([9., 7., 5., 3., 1.])).all()

    var = LoopVariable('int',mock.int_var, start=10, stop=1, step=-2)
    assert len(var) == 5
    assert (var.values == np.array([10., 8., 6., 4., 2.])).all()


def test_simple_loop_var(simple_loop):
    mock = Mock()
    var = LoopVariable('int',mock.int_var, start=1, stop=9, step=2)
    var.__iter__()
    values = list(var.values)
    pass
    assert (var.values == [1, 3, 5, 7, 9]).all()

def test_simple_loop(simple_loop):
    assert len(simple_loop) == 5

    i = 0

    for value in simple_loop:
        i += 1
        print(m.int_var, value, i)
        assert value is not None





