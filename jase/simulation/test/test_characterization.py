from ..variable import Variable
from ..loop_component import LoopComponent, LoopVariable
from ..base_component import BaseComponent

class Sim(BaseComponent):
    x = Variable(0)

    def execute(self):
        self.y = self.x*2


class Char(LoopComponent):

    
    sim = Sim()

s = Sim()

assert 'x' in Sim.params
assert 'x' in s.params
assert s.params['x'].name == 'x'

assert s.x == 0

s.execute()
assert self.y == 0