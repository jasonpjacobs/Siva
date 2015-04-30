
from .primitives import Primitive
from ...components.parameter import Float, String, File
from ...design import Pin, Net
from .save import V, I_src

class Source(Primitive):
    registry_name = "sources"

    @property
    def I(self):
        return I_src(self)

    @property
    def V(self):
        return V(self.p, self.n)


class Vdc(Source):
    token = "V"

    p = Pin()
    n = Pin('0')
    v = Float()
    ac = Float(optional=True)

    def __init__(self, p, n=None, v=1.0, ac=None):
        if n is None:
            n = Net(name='0')

        super().__init__(p=p, n=n, v=v, ac=ac)

    def card(self):
        dct = self.card_dict()
        if self.ac is not None:
            dct['ac'] = "AC {ac}".format(ac=self.ac)
        else:
            dct['ac'] = ''
        txt = "{name} {p} {n} {v}V {ac}".format(**dct)
        return [txt]

class Vpulse(Source):
    token = "V"

    p = Pin()
    n = Pin()
    v1 = Float(0.0)
    v2 = Float(1.0)
    delay = Float(0.)
    rise = Float(100e-12, optional=True)
    fall = Float(100e-12, optional=True)
    width = Float(500e-12, optional=True)
    period = Float(1e-9, optional=True)

    def __init__(self, p, n=None, v1=0, v2=1.0, delay=0, rise=None, fall=None, width=None, period=1e-9):

        assert p is not None
        if n is None:
            n = Net(name=0)
        if rise is None:
            rise = period/20.0
        if fall is None:
            fall = rise
        if width is None:
            width = (period - (rise+fall))/2

        super().__init__(p=p, n=n, v1=v1, v2=v2, delay=delay, rise=rise, fall=fall, width=width, period=period)


    def card(self):
        txt = "{name} {p} {n} PULSE({v1} {v2} {delay} {rise} {fall} {width} {period})".format(**self.card_dict())
        return [txt]


class Vpwl(Primitive):
    dc = Float()
    ac = Float()
    file = File()

    def __init__(self, p, n=0, ac=0, dc=0, name=None, file=None, points=None, path=None):
        super().__init__(p=p, n=n, ac=ac, dc=dc, name=name)
        self.file = file
        self.points = points

    def card(self):
        txt = super().card()
        points_txt = " ".join( ["{} {}".format( str(p[0]), str(p[1])) for p in self.points])
        txt += " PWL {}".format(points_txt)
        return txt


class Idc(Source):
    token = "I"

    p = Pin()
    n = Pin('0')
    i = Float()
    ac = Float(optional=True)

    def __init__(self, p, n=None, i=100e-6, ac=None):
        if n is None:
            n = Net(name='0')

        super().__init__(p=p, n=n, i=i, ac=ac)

    def card(self):
        dct = self.card_dict()
        if self.ac is not None:
            dct['ac'] = "AC {ac}".format(ac=self.ac)
        else:
            dct['ac'] = ''
        txt = "{name} {p} {n} {i} {ac}".format(**dct)
        return [txt]
