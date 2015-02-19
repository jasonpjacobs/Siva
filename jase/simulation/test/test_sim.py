import pytest

from ..variable import Variable
from ..loop_component import LoopComponent, LoopVariable
from ..base_component import BaseComponent
from ..measurement import Measurement

import time
import tempfile

class Sim(BaseComponent):
    x = Variable(10)
    m1 = Measurement(expr='self.y')

    def execute(self):
        print("Running ...", time.time())
        time.sleep(.01)
        self.y = self.x*2

class Char(LoopComponent):
    x=LoopVariable(name='x', start=1, stop=10, n=10, target='sim.x')
    sim = Sim()
    m1 = Measurement(expr='sim.m1')

def test_sim():
    s = Sim()

    assert 'x' in Sim.params
    assert 'x' in s.params
    assert s.params['x'].name == 'x'
    assert s.params['x'].value == 10

    assert s.x == 10

    s.execute()
    assert s.y == 20

    assert 'm1' in s.measurements

def test_char():
    work_dir = tempfile.mkdtemp()
    c = Char(name="Char", work_dir=work_dir, log_file="char.log")

    assert c is not None
    assert c.sim is not None
    assert 'x' in c.params

    assert 'x' in c.loop_vars
    assert 'sim' in c.namespace

    c.start()
    print(c.results)
    assert c.results is not None

def print_log(root):
    import os
    assert root.log_file is not None
    assert os.path.exists(root.log_file)
    txt = open(root.log_file,'r').readlines()
    print("".join(txt))



