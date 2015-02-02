import pytest

from ..base_component import BaseComponent

class MockComponent(BaseComponent):
    """  A mock comopnent class that records the order in which its methods were called
    """
    LOG = []
    def __init__(self,name=None):
        super().__init__(name=name)
        self.init_called = False
        self.reset_called = False
        self.exec_called = False
        self.measure_called = False
        self.final_called = False

    def init(self):
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
        pass
    B.add_instance(B, MockComponent(name='c'), name='c')

    class A(MockComponent):
        pass
    A.name = 'a'
    A.add_instance(A, B(name='b1'),name='b1')
    A.add_instance(A, B(name='b2'),name='b2')

    a = A(name='a')
    return a

def test_model(sim_tree):
    sim = sim_tree

    a = sim
    b1 = a.b1
    b2 = a.b2
    c1 = a.b1.c
    c2 = a.b2.c
    a.start()

    print(MockComponent.LOG)
    assert MockComponent.LOG == ['a.init',
                                   'b1.init',
                                     'c.init',
                                   'b2.init',
                                     'c.init',

                                 'a.exec',
                                   'b1.exec',
                                     'c.exec',
                                     'c.measure',
                                   'b1.measure',
                                   'b2.exec',
                                     'c.exec',
                                     'c.measure',
                                   'b2.measure',
                                 'a.measure',

                                     'c.final',
                                   'b1.final',
                                     'c.final',
                                   'b2.final',
                                 'a.final']




