import pytest

from ..variable import Variable
from ..loop_component import LoopComponent, LoopVariable
from ..base_component import BaseComponent
from ..measurement import Measurement

class Sim(BaseComponent):
    x = Variable(0)

    m1 = Measurement(expr='self.y')

    def execute(self):
        self.y = self.x*2

class Char(LoopComponent):
    x=LoopVariable(name='x', start=1, stop=10, n=10)
    sim = Sim()

def test_sim():
    s = Sim()

    assert 'x' in Sim.params
    assert 'x' in s.params
    assert s.params['x'].name == 'x'
    assert s.params['x'].value == 0

    assert s.x == 0

    s.execute()
    assert s.y == 0

    assert 'm1' in s.measurements

def Xtest_char():
    c = Char(name="Char")

    assert c is not None
    assert c.sim is not None
    assert 'x' in c.params

    assert 'x' in c.loop_vars
    assert 'sim' in c.namespace

    c.start()
    print(c.results)






