from jtypes import Typed, Str

class View(Typed):
    name = Str()
    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path