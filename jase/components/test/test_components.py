import pytest
import pdb

from jase.components.component import Component as jComponent
from ..parameter import Parameter

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

    # Update the occurrence of 'c'
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


@pytest.fixture
def hier_with_params():

    class C(Component):
        z = Parameter(923478)

    class B(Component):
        y = Parameter('234l')
        c = C()

    class A(Component):
        d = Parameter(167.2, local=True)
        z = Parameter(1111)
        b = B()

    a = A(name='a')
    return a

def test_component_namespaces(hier_with_params):
    a = hier_with_params
    assert a is not None

    ns = a.namespace

    assert ns is not None
    assert 'z' in ns
    assert a.namespace['z'] == 1111
    assert a.namespace['a'] == a


    # Local parameters should not show up in name spaces
    assert 'x' not in a.namespace


    assert a.namespace

def test_namespace_order(hier_with_params):
    a = hier_with_params

    # When called from C, the parameter value
    # should be C's z parameter (923478)
    assert a.b.c.namespace['z'] == 923478

    # But when called from 'A', it should be A's parameter 'z'
    assert a.namespace['z'] == 1111

def test_instance_naming():
    class C(Component):
        z = Parameter(923478)

    class B(Component):
        y = Parameter('234l')

    c = C()
    # The name keyword should override the instances name
    c.add_instance(B(name='b1'), name='b2')

    assert 'b2' in c._components

    assert c.b2.name == 'b2'













