from ..spice import Tran, Simulation, Include, Circuit, Primitive, Save
from ..spice.primitives import *
from ..spice.sources import Vpulse, Vdc
from ...design import Pin, Net, Input, Output

assert Include.registry_name == "includes"

"""
.INCLUDE P:\models\nmos_50n.model
.DC VVd 0 1.2 0.01
VVg g 0 0.5V
VVd d_s 0 1.0V
VVd_p d_s d 0V
VVdd vdd 0 1.5V
VVss vss 0 0.0V
MM1 d g vss vss n50n W=5e-08 L=5e-08 M=1
.PRINT dc FORMAT=RAW V(vdd) V(vss) V(g) V(d) I(rr1) I(VVd)
.END
"""

class Inv(Circuit):
    #vdd = Supply(domain="vdd_core")
    vdd = Net('vdd')
    vss = Net('vss')
    i = Input(name="in")
    o = Output()
    mp1 = Pmos(vdd, i, o, '0', w=2e-6, l=.35e-6, m=2, model="p50n")
    mn1 = Nmos(vss, i, o, '0', w=2e-6, l=.35e-6, m=2, model="n50n")


class Test(Simulation):
    """ A simple test circuit
    """


    Include(r"P:\models\nmos_50n.model")
    Tran(step=.2e-9, stop=10e-9)

    vdd = Net(name='vdd!')
    a = Net(name='a')
    b = Net(name='b')
    dut = Inv(a, b)

    r1 = R(a, b, r=50)
    c1 = C(a, b, c=10e-15)
    l1 = L(a, b, l=1e-9, ic=.1e-6)

    # Sources
    v1 = Vpulse(a, period=10e-9)
    V_vdd = Vdc(vdd, v=1.0)  # having vdd in quotes should create a net

    # Saves
    #Save(dut.i, type='v')



def test_something():
    t = Test()

    '''
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
    assert t.v1.width == 4.5e-09
    '''

    txt = t.netlist()
    print("\n".join(txt))
    assert False

