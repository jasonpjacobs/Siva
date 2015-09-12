import siva
from jtypes import Float, Int, Str

class Nmos(siva.Component):
    w = Float()
    l = Float()
    n = Int()
    model = Str()