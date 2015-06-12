import pytest
import tempfile
from siva.simulation.base_component import BaseComponent

class MockComponent(BaseComponent):
    """  A mock component class that records the order in which its methods were called
    """
    LOG = []

    def __init__(self,name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.init_called = False
        self.reset_called = False
        self.exec_called = False
        self.measure_called = False
        self.final_called = False

    def prepare(self):
        self.LOG.append("{}.prepare".format(self.name))

    def initialize(self):
        self.LOG.append("{}.init".format(self.name))
        self.init_called = True

    def reset(self):
        self.LOG.append("{}.reset".format(self.name))
        self.reset_called = True

    def execute(self):
        self.LOG.append("{}.exec".format(self.name))
        self.exec_called = True

    def measure(self, results=None):
        self.LOG.append("{}.measure".format(self.name))
        self.measure_called = True

    def final(self):
        self.LOG.append("{}.final".format(self.name))
        self.final_called = True

@pytest.fixture
def sim_tree():

    class B(MockComponent):
        c = MockComponent()

    class A(MockComponent):
        b1 = B()
        b2 = B()

    A.name = 'a'
    work_dir = tempfile.mkdtemp()
    a = A(name='a', work_dir=work_dir, log_file="sim.log")
    return a

@pytest.mark.xfail
def test_model(sim_tree):
    sim = sim_tree

    a = sim
    b1 = a.b1
    b2 = a.b2
    c1 = a.b1.c
    c2 = a.b2.c
    try:
        a.start()
    except:
        raise

    print(MockComponent.LOG)

    assert MockComponent.LOG == ['a.init',
                                 'a.exec',
                                   'b1.init',
                                   'b1.exec',
                                     'c.init',
                                     'c.exec',
                                     'c.measure',
                                     'c.final',
                                    'b1.measure',
                                    'b1.final',
                                   'b2.init',
                                     'b2.exec',
                                       'c.init',
                                       'c.exec',
                                       'c.measure',
                                       'c.final',
                                     'b2.measure',
                                     'b2.final',
                                   'a.measure',
                                 'a.final']