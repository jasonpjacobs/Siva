import pytest

from siva.design.design import Design
from siva.design.connections import Pin, Input, Output, Net
from siva.components import Parameter



print("Defining Nmos")
class Nmos(Design):
    s = Pin()
    g = Pin()
    d = Pin()
    b = Pin()

    w = Parameter()
    l = Parameter()
    m = Parameter()



print("Defining Inv")
class Inv(Design):
    in_ = Input(name="in")
    out = Output()

    #Net("s, g, d, b")

    #s = Net("s")
    n1 = Nmos(s, g, d, b, w=2, l=.35, m=2)


def test_design():
    print("Instantiating Buf")
    d = Inv(Net('i'), Net('o'))

    assert d is not None
    assert hasattr(d, "ports")

    assert "in_" in d.ports
    assert "out" in d.ports

    # Ensure the order of definition is preserved
    assert list(d.ports.values())[0] is d.ports["in_"]
    assert list(d.ports.values())[1] is d.ports["out"]

    # Check instances
    assert "n1" in d.instances
    assert list(d.children)[0].name == "n1"

    # Check nets
    assert "s" in d.nets
    assert "g" in d.nets
    assert "b" in d.nets
    assert "d" in d.nets

    # Check parameters
    assert d.n1.w == 2.0
    assert d.n1.l == 0.35
    assert d.n1.m == 2

    # Check parameter modification
    d.n1.w = 4.0
    assert d.n1.w == 4.0




