import tempfile

from siva.simulation.spice import Tran, Simulation, Include, Circuit, Primitive, Save
from siva.simulation.spice.primitives import *
from siva.simulation.spice.sources import Vpulse, Vdc
from siva.simulation.spice.connections import Net, Input, Output, GND

assert Include.registry_name == "includes"

Simulation.simulator_path = ''

def test_parse_results():
    type, path, net = Simulation.parse_results_entry('v(m.x_dut.m1_n#gate)')

    assert type == 'v'
    assert path == ['m', 'x_dut', 'm1_n']
    assert net == 'gate'

    type, path, net = Simulation.parse_results_entry('v(x_dut.vs_p)')
    assert type == 'v'
    assert path == ['x_dut']
    assert net == 'vs_p'

class Inv(Circuit):
    #vdd = Supply(domain="vdd_core")

    i = Input('i')
    o = Output('o')
    vdd = Input('vdd')
    a = Net('a')
    b = Net('b')
    mp1 = Pmos(s=vdd, g=i, d=o, b=GND, w=2, l=.35, m=2, model="p50n")
    mn1 = Nmos(s=GND, g=i, d=o, b=GND, w=2, l=.35, m=1, model="n50n")

    r1 = R(vdd, vddby2, r=100e3)
    r2 = R(vddby2, GND, r=100e3)


class Test(Simulation):
    """ A simple test circuit
    """
    Include(r"P:\models\nmos_50n.model")
    Tran(step=.2e-9, stop=10e-9)

    vdd = Net(name='vdd!')
    a = Net(name='a')
    b = Net(name='b')
    c = Net('c')
    d = Net('d')
    dut = Inv(a, b, vdd)

    r1 = R(b, c, r=50)
    c1 = C(d, GND, c=10e-15)
    l1 = L(c, d, l=1e-9, ic=.1e-6)

    # Sources
    v1 = Vpulse(a, period=10e-9)
    V_vdd = Vdc(vdd, v=1.2)

    # Saves
    Save(dut.mn1.pwr, dut.i.V, dut.vddby2.V)

@pytest.mark.xfail
def test_simulation():
    work_dir = tempfile.mkdtemp()
    t = Test(name='Simulation Test', work_dir=work_dir)
    assert t is not None
    assert len(t.analyses) > 0

    assert t.root is not None

    a = t.analyses[0]

    assert a.step == 0.2e-9
    assert a.stop == 10e-9
    assert len(t.sources) == 2
    assert 'v1' in t.sources
    assert t.v1 is t.sources['v1']
    assert t.v1.period == 10e-9
    assert t.v1.width == 4.5e-09
    assert t.saves[0].parent is t

    a = t.a
    assert a.parent is t
    assert a.V.p.parent is t

    assert t.dut.path == "X_dut"
    assert t.dut.o.path == "X_dut:o"

    t.start()

