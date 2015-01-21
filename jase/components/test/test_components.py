import pytest

from jase.components.component import Component as jComponent

class Component(jComponent):
    def __init__(self, parent=None, children=None, id=None):
        self.id = id
        super().__init__(parent, children)

class C(Component):
    pass

class B(Component):
    c = C(id=104)

class A(Component):
    b = B()

@pytest.fixture
def model():
    return A()

def test_paths(model):
    print(type(model.b.c))
    assert model.b.c.id == 104

if True:
    import pdb
    c = C()


pdb.set_trace()
#test_paths(model())