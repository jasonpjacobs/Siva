import pytest

from ..registered import Registered, Registry
from ..component import Component

class Var(Registered):
    registry_name = "my_vars"


def test_component_dict():

    d = Registry(owner=None)
    v = Var()
    v.name = 'a'
    d["a"] = v


    d2 = d.clone()
    assert "a" in d
    assert "a" in d2

    assert d["a"] is not d2["a"]


def test_registry():

    class A(Component):
        v1 = Var()

    assert "my_vars" in A._registries
    assert 'v1' in A.my_vars

    # Create an instance of A
    a = A(name='a')
    assert "my_vars" in a._registries
    assert 'v1' in a.my_vars

    a.my_vars["v1"].parent is a

    assert a.my_vars is not A.my_vars

    assert a.v1 is a.my_vars["v1"]
    assert a.my_vars["v1"] is not A.my_vars["v1"]

    assert a.v1 is not A.v1

