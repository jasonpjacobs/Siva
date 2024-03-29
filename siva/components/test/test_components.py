import pytest
import pdb

from siva.components.component import Component as jComponent
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

    c = C(name='c')
    c.id = 104


    b = B(children=[c,])

    a = A()
    a.add_instance(b, 'b')

    # Add instances w/o a name
    a.add_instance(C()) # Should get the name i2
    a.add_instance(C(name='c2'))
    return a




def test_instantiation(model):
    a = model

    # Check that the child component was put into the _components dict
    assert 'b' in A.components

    # Check that A's component dict was copied to the 'a' instance.
    assert 'b' in a.components

    # Check that the child component can be looked up via standard attribute access
    assert a.b is a.components['b']

    # Same for the component in the class definition
    assert A.b is A.components['b']

    # Check that the instance child is a copy of the class
    # in the class definition
    assert a.components['b'] is not A.components['b']
    assert a.b is not A.b

def test_procedural_model(procedural_model):
    test_instantiation(procedural_model)

    a = procedural_model

    assert len(a.components) == 3
    assert 'i2' in a.components
    assert 'c2' in a.components

def test_paths(model):
    a = model
    assert repr(a) == 'A(name=a)'


    assert set([c.name for c in a.children]) == set([c.name for c in a.components.values()])

    assert a.b.c.id == 104

    # Update the occurrence of 'c'
    a.b.c.id = 0

    assert A.b.c.id == 104
    assert a.b.c.id == 0

    pc = a.b.c.path_components
    assert(len(pc) == 3)
    assert pc[0] is model
    assert pc[1] is a.b
    assert pc[2] is a.b.c




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
    assert a.root is a

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


def hier_with_params_procedural():
    """ Procedurally create a component hierarchy for testing.
    """


    c = Component(params = Parameter(923478, name='z'))

    b = Component(name='b',
                  params=[
                      Parameter('234l',name='z')
                  ],
        children=[c,])

    a = Component(name='a',
                  params=[
                      Parameter(167.2, local=True, name='d'),
                      Parameter(1111, name='z')
                  ],
                  children=[b,])


@pytest.fixture
def a(hier_with_params):
    return hier_with_params

def test_component_namespaces(a):
    assert a is not None

    ns = a.namespace

    assert ns is not None
    assert 'z' in ns
    assert a.namespace['z'] == 1111
    assert a.namespace['a'] == a

    # Local parameters should not show up in name spaces
    assert 'x' not in a.namespace
    assert a.namespace

def test_namespace_order(a):

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

    assert 'b2' in c.components
    assert c.b2.name == 'b2'


def test_clone(a):

    a2 = a.clone(name='a2')

    assert a2.name == 'a2'
    assert a.b is not a2.b
    assert a.b.c is not a2.b.c
    assert a2.b.c.parent is not a.b
    assert a2.b.c.parent is a2.b

@pytest.mark.skipif(True, reason="Not implemented")
def test_procedural_model(procedural_model):
    a = procedural_model
    test_clone(a)
    test_namespace_order(a)



def test_param_descriptors(a):
    assert a.d == 167.2
    a.d = 42.3
    assert a.d == 42.3
    assert a.params['d'].value == 42.3










