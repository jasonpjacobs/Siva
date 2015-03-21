import pytest
import unittest

from ..spice import Tran, Simulation, Include
from ..spice.sources import Vpulse
from ...design import Design, Pin, Net, Input, Output
from ...components import Parameter

from ...simulation.save import Save

assert Include.registry_name == "includes"

class Nmos(Design):
    s = Pin()
    g = Pin()
    d = Pin()
    b = Pin()

    w = Parameter()
    l = Parameter()
    m = Parameter()


class Inv(Design):
    in_ = Input(name="in")
    out = Output()
    n1 = Nmos(s, g, d, b, w=2, l=.35, m=2)

class Test(Simulation):
    Include(r"P:\models\nmos_50n.model")
    Tran(step=0.2, stop=10e-9)

    i = Net(name='i')
    o = Net(name='o')
    dut = Inv(i, o)

    # Sources
    v1 = Vpulse(i, period=10e-9)

    # Saves
    Save(dut.in_,type='v')



def test_something():
    t = Test()


    assert t is not None

    assert len(t.analyses) > 0

    a = t.analyses["tran"]

    assert a.step == 0.2
    assert a.stop == 10e-9

    assert len(t.saves) is not None
    print(t.saves)

    assert len(t.sources) == 1

    assert 'v1' in t.sources
    assert t.v1 is t.sources['v1']

    assert t.v1.period == 10e-9
    assert t.v1.pw == 500e-9


    txt = t.netlist()
    print(txt)
    assert False

