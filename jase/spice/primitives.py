
from .descriptors import NodeType, FloatType, Int, StringType, Type
from .command import Command
import pdb

class Primitive(Command):
    def parse_kwargs(self, kwargs):
        for key, value in kwargs.items():
            if key in self.__class__.__dict__:
                setattr(self, key, value)

    @property
    def path(self):
        if hasattr(self, '_path'):
            if self._path:
                return self._path + ":" + self.token + self.name
        return self.name

    @path.setter
    def path(self, value):
        self._path = value


class Vdc(Primitive):

    p = NodeType()
    n = NodeType(0)
    v = FloatType()

    def __init__(self, p=None, n=0, v=0, name=None, path=None):
        self.p = p
        self.n = n
        self.v = v
        self.name = name
        self._path = path

    def card(self):
        txt = "V{name} {p} {n} {v}V".format(name=self.name, p=self.p, n=self.n, v=self.v)
        return txt

class Vsrc(Primitive):
    token = "V"
    p = NodeType()
    n = NodeType()
    dc = FloatType(None)
    ac = FloatType(None)

    def __init__(self, p, n, dc=None, ac=None, name=None, path=None):
        self.p = p
        self.n = n
        self.dc = dc
        self.ac = ac
        self.name = name
        self._path = path

    def card(self):
        dc = "DC {}".format(str(self.dc)) if self.dc is not None else ""
        ac = "AC {}".format(str(self.ac)) if self.ac is not None else ""
        txt = "V{} {} {} {} {}".format(self.name, self.p, self.n, dc, ac)
        return txt

class Vsin(Vsrc):
    dc = FloatType()
    ac = FloatType()
    amp = FloatType()
    freq = FloatType()
    delay = FloatType()
    theta = FloatType()
    offset = FloatType()

    def __init__(self, p, n=0, ac=None, dc=None, amp=amp, freq=freq, delay=0, theta=0, offset=0, name=None, path=None):
        super().__init__(p=p, n=n, ac=ac, dc=dc, name=name)
        self.amp = amp
        self.freq = freq
        self.delay = delay
        self.theta = theta
        self.offset = offset
        self._path = path

    def card(self):
        txt = super().card()
        txt += " SIN({} {} {} {} {})".format(self.offset, self.amp, self.freq, self.delay, self.theta)
        return txt

class Vpulse(Vsrc):
    v1 = FloatType()
    v2 = FloatType()
    delay = FloatType()
    rise = FloatType()
    fall = FloatType()
    width = FloatType()
    period = FloatType()

    def __init__(self, p, n=0, ac=None, dc=None, v1=0, v2=None, delay=0, rise=None, fall=None,
                 width=None, period=None, name=None, path=None):
        super().__init__(p=p, n=n, ac=ac, dc=dc, name=name)
        self.v1 = v1
        self.v2 = v2
        self.delay = delay
        self.rise = rise
        self.fall = fall
        self.width = width
        self.period = period
        self._path = path

    def card(self):
        txt = super().card()
        txt += " PULSE({} {} {} {} {} {} {})".format(self.v1, self.v2, self.delay, self.rise, self.fall,
                                               self.width, self.period, path=None)
        return txt

class Vpwl(Vsrc):
    dc = FloatType()
    ac = FloatType()
    file = StringType()

    def __init__(self, p, n=0, ac=0, dc=0, name=None, file=None, points=None, path=None):
        super().__init__(p=p, n=n, ac=ac, dc=dc, name=name)
        self.file = file
        self.points = points


    def card(self):
        txt = super().card()
        points_txt = " ".join( ["{} {}".format( str(p[0]), str(p[1])) for p in self.points])
        txt += " PWL {}".format(points_txt)
        return txt

class R(Primitive):
    token = "R"
    p = NodeType()
    n = NodeType()
    r = FloatType()

    def __init__(self, p=None, n=None, r=1e3, name=None, path=None):
        self.p = p
        self.n = n
        self.r = r
        self.name = name
        self._path = path

    def card(self):
        txt = "R{name} {p} {n} R={r}".format(name=self.name, p=self.p, n=self.n, r=self.r)
        return txt

class C(Primitive):
    token = "C"
    p = NodeType()
    n = NodeType()
    c = FloatType()

    model = StringType()
    ic = FloatType()
    w = FloatType()
    l = FloatType()
    tc1 = FloatType()
    tc2 = FloatType()
    temp = FloatType()

    def __init__(self, p=None, n=None, c=1e-12, name=None, path=None, **kwargs):
        self.p = p
        self.n = n
        self.c = c
        self.name = name
        self._path = path
        self.parse_kwargs(kwargs)

    def card(self):
        txt = "C{name} {p} {n} C={c}".format(name=self.name, p=self.p, n=self.n, c=self.c)
        return txt

class L(Primitive):
    token = "L"
    p = NodeType()
    n = NodeType()
    l = FloatType()

    ic = FloatType()
    tc1 = FloatType()
    tc2 = FloatType()
    temp = FloatType()

    def __init__(self, p=None, n=None, l=1e-9, name=None, path=None):
        self.p = p
        self.n = n
        self.l = l
        self.name = name
        self._path = path

    def card(self):
        txt = "L{name} {p} {n} L={l}".format(name=self.name, p=self.p, n=self.n, l=self.l)
        return txt

class Nmos(Primitive):
    token = "M"
    s = NodeType()
    g = NodeType()
    d = NodeType()
    b = NodeType()

    l = FloatType()
    w = FloatType()
    m = Int()

    model = StringType()


    def __init__(self, d=None, g=None, s=None, b=None, w=None, l=None, m=1, model=None, name=None, path=None):
        self.s = s
        self.g = g
        self.d = d
        self.b = b
        self.w = w
        self.l = l
        self.m = m
        self.model = model
        self.name = name
        self._path = path


    @property
    def nodes(self):
        return( (self.s, self.g, self.d, self.b))

    def card(self):
        txt = "M{} {} {} {} {} {}".format(self.name, str(self.d), str(self.g), str(self.s), str(self.b), str(self.model))

        if self.w:
            txt += " W={}".format(self.w)

        if self.l:
            txt += " L={}".format(self.l)

        if self.m:
            txt += " M={}".format(self.m)
        return txt

