import pytest

from ..base_component import BaseComponent

class B(BaseComponent):
    pass

class A(BaseComponent):
    b = B()


def test_clone():
    b = B()

    c = b.clone()

    assert b.master is b
    assert c.master is c
    assert b.master is not c.master

def test_root():
    a = A(name='a')

    assert hasattr(A, 'root')

    assert a.root is a
    assert a.b.root is a


