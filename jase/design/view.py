from jtypes import Typed

class View(Typed):
    pass

    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path