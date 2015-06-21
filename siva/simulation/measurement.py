import collections
from ..components.registered import Registered

class Measurement(Registered):
    registry_name = "measurements"

    def __init__(self, expr, name=None, spec=None):
        self.name = name
        self.expr = expr
        self.spec = spec
        self.value = None

    def _store(self, class_dct, registry_name):
        self._store_as_key_value_pair(class_dct, registry_name)

    def __set__(self, instance, value):
        instance.measurements[self.name].value = value

    def __get__(self, instance, owner):
        if instance is not None:
            return instance.measurements[self.name].value
        else:
            return owner.measurements[self.name].value

    def evaluate(self, namespace):
        try:
            self.value = eval(self.expr, globals(), namespace)
        except Exception as e:
            self.value = e.args
            raise
        return self.value
