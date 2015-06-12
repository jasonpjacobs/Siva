import pytest


from siva.components.parameter import Parameter
from siva.simulation.loop_component import LoopComponent, LoopVariable
from siva.simulation.base_component import BaseComponent
from siva.simulation.measurement import Measurement

import time
import tempfile

class Sim(BaseComponent):
    x = Parameter(10)
    m1 = Measurement(expr='self.y')

    def execute(self):
        print("Running ...", time.time())
        time.sleep(.1)
        self.y = self.x*2

class Char(LoopComponent):
    x=LoopVariable(name='x', start=1, stop=10, n=10, target='sim.x')
    sim = Sim()
    m1 = Measurement(expr='sim.m1')

@pytest.mark.skipif(False, reason="Isolating debug case")
def test_sim():
    s = Sim()

    assert 'x' in Sim.params
    assert 'x' in s.params
    assert s.params['x'].name == 'x'
    assert s.params['x'].value == 10

    assert s.x == 10

    s.execute()
    assert s.y == 20

    s.measure()
    assert 'm1' in s.measurements

    assert s.measurements['m1'].value == 20
    assert s.m1 == 20



def test_char():
    work_dir = tempfile.mkdtemp()

    work_dir = r'P:\work\test_sim'
    import os, shutil
    if len(os.listdir(work_dir)):
        for file_object in os.listdir(work_dir):
            file_object_path = os.path.join(work_dir, file_object)
            if os.path.isfile(file_object_path):
                os.remove(file_object_path)
            else:
                shutil.rmtree(file_object_path)
    import os

    print("Work dir is", work_dir)
    c = Char(name="Char", work_dir=work_dir, log_file="char.log")

    assert c is not None
    assert c.sim is not None
    assert 'x' in c.params


    assert 'loop_vars' in c._registries
    assert 'loop_vars' in Char._registries

    assert 'x' in c.loop_vars
    assert 'sim' in c.namespace

    c.start()
    print(c.results)
    assert c.results is not None

    assert set(c.results.columns) == set(["x", "m1"])
    assert len(c.results) == 10

    print(c.results)

    i=0
    for row in c.results:
        assert row['m1'] == (i+1)*2.
        i += 1


def print_log(root):
    import os
    assert root.log_file is not None
    assert os.path.exists(root.log_file)
    txt = open(root.log_file,'r').readlines()
    print("".join(txt))



