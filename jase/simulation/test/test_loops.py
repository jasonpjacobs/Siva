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
    a = LoopVariable('int', 'obj.int_var', start=1, stop=9, step=2)  # 5 values: 1,3,5,7, and 9
    b = LoopVariable('float', 'obj.float_var', start=-2., stop=2., n=3 )
    c = LoopVariable('str', 'obj.str_var', values=['"A"', '"B"', '"C"'])

    loop = LoopComponent(parent=None, vars=[a,b,c], namespace={'obj': mock})
    return loop

def test_loop_creation(mock):
    var = LoopVariable('int','mock.int_var', start=1, stop=9, step=2)
    assert len(var) == 5
    assert (var.values == np.array([1, 3, 5, 7, 9])).all()

    var = LoopVariable('int',mock.int_var, start=1, stop=10, step=2)
    assert len(var) == 5
    assert (var.values == np.array([1, 3, 5, 7, 9])).all()

    var = LoopVariable('int',mock.int_var, start=9, stop=1, step=-2)
    assert len(var) == 5
    assert (var.values == np.array([9., 7., 5., 3., 1.])).all()

    var = LoopVariable('int',mock.int_var, start=10, stop=1, step=-2)
    assert len(var) == 5
    assert (var.values == np.array([10., 8., 6., 4., 2.])).all()

    var = LoopVariable('str', 'mock.str_var', values = ['a','b','c'])
    assert len(var) == 3

def test_simple_loop(simple_loop):
    assert len(simple_loop) == 45

    m = simple_loop.__namespace__['obj']
    i = 0

    results = {}
    results['int'] = []
    results['str'] = []
    results['float'] = []
    for value in simple_loop:
        i += 1
        results['int'].append(m.int_var)
        results['str'].append(m.str_var)
        results['float'].append(m.float_var)

    # This is the outer loop variable,
    # So there should be 3*3 (9) unique
    # values
    int = np.array(results['int'])
    assert int.max() == 9
    assert int.min() == 1
    assert len(int[int == 5]) == 9
    print(int[0:9])
    assert (int[0:9] == np.ones(9)).all()
    assert (int[9:18] == 3*np.ones(9)).all()

    flt = np.array(results['float'])
    assert flt.min() == -2
    assert flt.max() == 2
    assert len(flt[flt==0]) == 15
    # Middle loop variable.  Should repeat 3 times, once for each value of str_val
    assert (flt[0:10] == [-2., -2., -2.,  0.,  0.,  0.,  2.,  2.,  2., -2. ]).all()

    # Inner loop variable.  Should iterate with every loop iteration, repeating
    # 5x3 times
    str = np.array(results['str'])
    assert (str[0:4] == ['A', 'B', 'C', 'A']).all()
    assert len(str[str=='A']) == 15













