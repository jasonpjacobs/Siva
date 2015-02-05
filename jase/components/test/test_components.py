import pytest
import pdb

from jase.components.component import Component as jComponent

class Component(jComponent):
    def __init__(self, parent=None, children=None, id=None, name=None):
        self.id = id
        super().__init__(parent, children, name=name)

class C(Component):
    pass

class B(Component):
    c = C(id=104,name='c')

class A(Component):
    b = B(name='b')

@pytest.fixture
def model():
    return A(name='a')

@pytest.fixture
def procedural_model():

    class A(Component):
        pass

    class B(Component):
        pass

        def run(self):
            a.int = 2

    c = C()
    c.id = 104

    b = B()
    b.add_instance(c, 'c')

    a = A()
    a.add_instance(b, 'b')

    return a




def test_instantiation(model):
    a = model

    # Check that the child component was put into the _components dict
    assert 'b' in A._components

    # Check that A's component dict was copied to the 'a' instance.
    assert 'b' in a._components

    # Check that the child component can be looked up via standard attribute access
    assert a.b is a._components['b']

    # Same for the component in the class definition
    assert A.b is A._components['b']

    # Check that the instance child is a copy of the class
    # in the class definition
    assert a._components['b'] is not A._components['b']
    assert a.b is not A.b

def test_procedural_model(procedural_model):
    test_instantiation(procedural_model)

def test_paths(model):
    assert model.b.c.id == 104

    # Update the occurance of 'c'
    model.b.c.id = 0

    assert A.b.c.id == 104
    assert model.b.c.id == 0


def test_model_modification():

    # Lets create one model
    model_A = A(name='a')

    # ... and make sure the defaults are correct.
    assert model_A.b.c.id == 104

    # Now change the definition of the instance 'c'
    B.c.id = 22

    # If we instantiate a new version of B, we should
    # get an id of 22
    b = B()
    assert b.c.id == 22

    # If we create a new A model
    model_B = A(name='a')

    # ... the B instance should still be the same
    assert model_B.b.c.id == 104



def test_hierarchy():
    a = A(name='a')
    assert a.b.parent is a
    assert a.b.c.parent is a.b

    assert a.b.c.root is a
    assert a.b.root is a

    assert a.b.c.path == 'a.b.c'






