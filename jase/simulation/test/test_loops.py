import pytest
import logging
import os


import numpy as np
from ..loop_component import LoopVariable, LoopComponent
from ..measurement import Measurement
from ...simulation.variable import Variable
import copy
LOG = []
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
    """

    A       B       C
    ================================
    1       -2      A
    5       -2      A
    9       -2      A
    1        0      A
    5        0      A
    9        0      A
    1        2      A
    5        2      A
    9        2      A
    1       -2      B
    5       -2      B
    9       -2      B
    1        0      B
    5        0      B
    9        0      B
    1        2      B
    5        2      B
    9        2      B
    """
    a = LoopVariable(name='int', target='Loop.int_var', start=1, stop=9, step=2)
    b = LoopVariable(name='float', target='Loop.float_var', start=-2., stop=2., n=3 ) # 3 values: -2, 0, 2
    c = LoopVariable(name='str', target='Loop.str_var', values=['A', 'B', 'C'])

    m1 = Measurement(name='int_result', expr='Loop.int_var')
    m2 = Measurement(name='float_result', expr='Loop.float_var')
    m3 = Measurement(name='str_result', expr='Loop.str_var')

    loop = LoopComponent(parent=None, vars=[a,b,c], name='Loop', measurements=[m1, m2, m3])
    return loop

def test_loop_variable_creation(mock):
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

def test_loop_variable_copy():
    v1 = LoopVariable('int','mock.int_var', start=1, stop=9, step=2)
    import copy
    v2 = copy.copy(v1)

    assert v1 is not v2

def test_loop_component_copy():



    a = LoopVariable(name='int_var', target='Loop.int_var', start=1, stop=9, step=2)
    m1 = Measurement(name='m1', expr='Loop.int_var')

    l2 = LoopComponent(parent=None, vars=None, name='l2', measurements=None)


    l1 = LoopComponent(parent=None, vars=[a,], name='l1', measurements=[m1], children=[l2,])



    assert 'int_var' in l1.params
    assert 'm1' in l1.measurements

    l2 = l1.clone()
    assert 'int_var' in l2.params
    assert 'm1' in l2.measurements

    assert l1.measurements['m1'] is not l2.measurements['m1']



def test_callable_loop_variable():

    class Mock:
        def __init__(self, value=0, name='M'):
            self.value=value
            self.name=name

        def set_value(self, value):
            self.value = value

    m = Mock(name='M')
    ms = Measurement('Loop.M.value', name='v')
    var = LoopVariable(name='var', target='Loop.M.set_value', values=[0.33, 0.55, 0.77])
    loop = LoopComponent(vars = [var,], name='Loop', measurements=[ms,])
    loop.M = m
    results = []
    loop.start()
    loop.wait()

    assert loop.results is not None

    results = np.array(loop.results['var'])
    assert results[0] == 0.33
    assert results[1] == 0.55
    assert results[2] == 0.77

def test_simple_loop(simple_loop):
    assert len(simple_loop) == 45

    loop = simple_loop

    assert 'int_result' in loop.measurements
    assert 'float_result' in loop.measurements
    assert 'str_result' in loop.measurements

    loop.start()
    loop.wait()
    results = loop.results


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


@pytest.fixture
def hierarchical_loops(mock):
    import tempfile
    work_dir = tempfile.mkdtemp()
    global M
    M = mock
    m1 = Measurement(name='m1', expr='l3.int_var')
    m2 = Measurement(name='m2', expr='l3.float_var')
    m3 = Measurement(name='m3', expr='l3.str_var')

    l1 = Measurement(name='l1', expr='"L1"')
    l2 = Measurement(name='l2', expr='"L2"')


    a = LoopVariable(name='int', target='l3.int_var', start=1, stop=9, step=2)
    b = LoopVariable(name='float', target='l3.float_var', start=-2., stop=2., n=3, endpoint=True)
    c = LoopVariable(name='str',  target='l3.str_var', values=['"A"', '"B"', '"C"'])

    L3 = LoopComponent(parent=None, vars=[c,], name='l3', measurements=[m1,m2,m3])
    L2 = LoopComponent(parent=None, vars=[b,], name='l2', children=[L3,], measurements=[l2,])
    L1 = LoopComponent(parent=None, vars=[a,], name='l1', children=[L2,],
                       work_dir=work_dir, measurements=[l1,], log_file='loop.log')

    from ...resources.disk_resources import LocalDiskManager

    L1.root_dir = work_dir
    L1.disk_mgr = LocalDiskManager(root=work_dir)
    return L1


def test_hierarchical_loops(hierarchical_loops):
    loop = hierarchical_loops
    loop.namespace

    try:
        loop.start()
    except KeyboardInterrupt:
        pass
        log = logging.getLogger('Disk')
        print("Log is", log, loop.disk_mgr.logger)
        log.error("Interrupted.")

    log_path = os.path.join(loop.root_dir, "disk_mgr.log")
    print(loop.log_file)
    print(loop.l2.l3.results)

    assert True






