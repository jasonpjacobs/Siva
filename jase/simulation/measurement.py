import collections
from ..components.component import ComponentDict

class Measurement:
    def __init__(self, expr, name=None, spec=None):
        self.name = name
        self.expr = expr
        self.spec = spec
        self.value = None

    def register(self, parent, dct, name=None):
        """Called by the Component metaclass to add child Components
        to the class's "measurements" dictionary
        """
        if name is not None:
            self.name = name

        self.parent = parent
        if "measurements" not in dct:
            dct["measurements"] = collections.OrderedDict()
        dct["measurements"][self.name] = self

    def __set__(self, instance, value):
        instance.measurements[self.name].value = value

    def __get__(self, instance, owner):
        if instance is not None:
            return instance.measurements[self.name]
        else:
            return owner.measurements[self.name]

    def evaluate(self, namespace):
        try:
            self.value = eval(self.expr, globals(), namespace)
        except Exception as e:
            self.value = e.args
            #raise
        return self.value


