

class Measurement:
    def __init__(self, name, expr, spec=None):
        self.name = name
        self.expr = expr
        self.spec = spec

    def evaluate(self, namespace):
        self.value = eval(self.expr, globals(), namespace)
        return self.value

