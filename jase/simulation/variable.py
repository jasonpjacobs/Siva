class Variable:
    def __init__(self, name, target, desc=None):
        self.name = name
        self.target = target
        self.desc = desc

    def eval(self, globals, locals):
        target = eval(self.target, globals, locals)
        if callable(target):
            exec("{}({})".format(self.target, self.value), globals, locals)
        else:
             exec("{}={}".format(self.target, self.value), globals, locals)
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value