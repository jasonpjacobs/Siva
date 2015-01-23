import pytest
import pdb

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


def test_instantiation():
    a = A()

    # Check that the child component was put into the _components dict
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


def test_paths(model):
    assert model.b.c.id == 104

    # Update the occurance of 'c'
    model.b.c.id = 0

    assert A.b.c.id == 104
    assert model.b.c.id == 0


def test_model_modification():

    # Lets create one model
    model_A = A()

    # ... and make sure the defaults are correct.
    assert model_A.b.c.id == 104

    # Now change the definition of the instance 'c'
    B.c.id = 22

    # If we instantiate a new version of B, we should
    # get an id of 22
    b = B()
    assert b.c.id == 22

    # If we create a new A model
    model_B = A()

    # ... the B instance should still be the same
    assert model_B.b.c.id == 104








