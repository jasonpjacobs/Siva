from ...components import Component
from ...components.parameter import Float

class Source(Component):
    registry_name = "sources"

class Vpulse(Source):
    v1 = Float(0.0)
    v2 = Float(1.0)
    td = Float(100e-12)
    tf = Float(100e-12)
    pw = Float(500e-12)
    period = Float(1e-9)

    def __init__(self, p, n=None, v1=0, v2=1.0, td=100e-12, tf=100e-12, pw=500e-9, period=1e-9):
        self.p = p
        self.n = n
        self.v1 = v1
        self.v2 = v2
        self.td = td
        self.tf = tf
        self.pw = pw
        self.period = period

    def card(self):
        dct = dict(self._param_dict)
        dct['name'] = self.name
        dct['p'] = self.p.net.name

        if self.n is not None:
            dct['n'] = self.n.net.name
        else:
            dct['n'] = "0"

        txt = "V_{name} {p} {n} PULSE({v1} {v2} {td} {tf} {pw} {period})".format(**dct)
        return [txt]


