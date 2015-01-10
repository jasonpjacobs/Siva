import jase
from jtypes import Float, Int, Str

class Nmos(jase.Component):
    w = Float()
    l = Float()
    n = Int()
    model = Str()