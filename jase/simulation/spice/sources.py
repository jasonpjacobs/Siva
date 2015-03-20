from ...components import Component
from ...components.parameter import Float

class Source(Component):
    dict_name = "sources"

class Vpulse(Source):
    v1 = Float(0.0)
    v2 = Float(1.0)
    td = Float(100e-12)
    tf = Float(100e-12)
    pw = Float(500e-12)
    period = Float(1e-9)

    def __init__(self, *nodes, v1=0, v2=1.0, td=100e-12, tf=100e-12, pw=500e-9, period=1e-9):
        self.nodes = nodes
        self.v1 = v1
        self.v2 = v2
        self.td = td
        self.tf = tf
        self.pw = pw
        self.period = period