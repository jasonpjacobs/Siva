from ...design.design import Design, DesignMeta
from .connections import Net, Pin
from ...components.parameter import Parameter, Float, String
from ...components.component import ComponentNamespace
from .save import Power, V, I

__all__ = ['Nmos', 'Pmos', 'R', 'L', 'C']

class SpiceMeta(DesignMeta):
    @classmethod
    def __prepare__(metacls, name, bases):
        return ComponentNamespace(default=Net)

class Primitive(Design, metaclass=SpiceMeta):
    prefix = ""

    def card(self):
        raise NotImplementedError

    def instance_designs(self, dct=None):
        """Primitives have no instances, by definition.
        """
        return dct

    def subckt_card(self):
        return None

    def card_dict(self):
        """Returns a dictionary of the primitive's name, connections, and parameters for netlist formatting."""
        dct = dict(self._param_dict)

        # Figure out our name
        if self.name[0].upper().startswith(self.token.upper()):
            dct['name'] = self.token + self.name[1:]
        else:
            dct['name'] = self.token + '_' + self.name

        for pin in self.ports.values():
            dct[pin.name] = pin.conn.name

        return dct

    def params_txt(self):
        """Returns a txt string consisting of parameter "Name=Value" pairs.  For netlisting."""
        value = self.card_dict()
        words = []
        for param in self.params.values():
            if not param.optional and param.value is None:
                words.append("{}={}".format(param.name, value[param.name]))
        return " ".join(words)

    @property
    def path(self, format=None):
        if format is None:
            return super().path
        if format == "spice":
            return super().path



class Mos(Primitive):
    token = "M"

    s = Pin()
    g = Pin()
    d = Pin()
    b = Pin()

    w = Float()
    l = Float()
    m = Parameter()
    model = String('nmos')

    def card(self):
        txt = "{name} {s} {g} {d} {b} {model} w={w} l={l} m={m}".format(**self.card_dict())
        return [txt]

    # Output/measurement requests
    @property
    def pwr(self):
        return Power(p=self.d, n=self.s)

class Nmos(Mos):
    """N-type MOSFET"""
    type = "N"


class Pmos(Mos):
    """P-type MOSFET"""
    type = "P"

class R(Primitive):
    """ Ideal resistor
    """
    token ="R"

    p = Pin()
    n = Pin()
    r = Float()

    def card(self):
        txt = "{name} {p} {n} R={r}".format(**self.card_dict())
        return [txt]


class C(Primitive):
    """Ideal capacitor
    """
    token ="C"
    p = Pin()
    n = Pin()
    c = Float()
    ic = Float(0, optional=True)

    def card(self):
        txt = "{name} {p} {n} C={c}".format(**self.card_dict())
        return [txt]


class L(Primitive):
    token = "L"
    p = Pin()
    n = Pin()
    l = Float()

    ic = Float(0, optional=True)
    tc1 = Float(optional=True)
    tc2 = Float(optional=True)
    temp = Float(optional=True)

    def card(self):
        txt = "{name} {p} {n} L={l}".format(**self.card_dict())
        return [txt]
