from ..spice import Tran, Simulation, Include, Circuit, Primitive, Save
from ..spice.sources import Vpulse
from ...design import Pin, Net, Input, Output
from ...components import Parameter
from ...components.parameter import String, Float

assert Include.registry_name == "includes"

class Nmos(Primitive):
    s = Pin()
    g = Pin()
    d = Pin()
    b = Pin()

    w = Float()
    l = Float()
    m = Parameter()

    model = String('nmos')

    def card(self):
        args = self._param_dict
        args['name'] = self.name
        args['s'] = self.s.net.name
        args['g'] = self.g.net.name
        args['d'] = self.d.net.name
        args['b'] = self.b.net.name
        txt = "m{name} {s} {g} {d} {b} {model} w={w} l={l} m={m}".format(**args)
        return txt

class Inv(Circuit):
    i = Input(name="in")
    o = Output()
    n1 = Nmos(s, g, d, b, w=2e-6, l=.35e-6, m=2)

class Test(Simulation):
    """ A simple test circuit
    """
    Include(r"P:\models\nmos_50n.model")
    Tran(step=.2e-9, stop=10e-9)

    a = Net(name='a')
    b = Net(name='b')
    dut = Inv(a, b)

    # Sources
    v1 = Vpulse(a, period=10e-9)

    # Saves
    Save(dut.i, type='v')



def test_something():
    t = Test()


    assert t is not None

    assert len(t.analyses) > 0

    a = t.analyses[0]

    assert a.step == 0.2e-9
    assert a.stop == 10e-9

    assert len(t.saves) is not None

    assert len(t.sources) == 1

    assert 'v1' in t.sources
    assert t.v1 is t.sources['v1']

    assert t.v1.period == 10e-9
    assert t.v1.pw == 500e-9


    txt = t.netlist()
    print("\n".join(txt))
    assert False

