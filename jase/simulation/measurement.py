

class Measurement:
    def __init__(self, name, expr, spec=None):
        self.name = name
        self.expr = expr
        self.spec = spec
        self.value = None

    def evaluate(self, namespace):
        self.value = exec(self.expr, globals(), namespace)
        return self.value

