

class Measurement:
    def __init__(self, name, expr, spec=None):
        self.name = name
        self.expr = expr
        self.spec = spec
        self.value = None

    def evaluate(self, namespace):
        try:
            self.value = eval(self.expr, globals(), namespace)
        except Exception as e:
            self.value = e.args
            #raise
        return self.value

