import inspect
from ..components.registered import Registered
class Parameter(Registered):
    """ A class to define Component level attributes.

    Parameter can be declared as pat of a class definition using a declarative syntax:

    class A(Component):
        # Define a parameter named 'b'
        b = Parameter()

    a = A()
    a.b = 2 # Sets the parameter value to 2

    """

    # When instantiated as part of a Component's class dictionary, this Param
    # will be stored in a dictionary named "dict_name"
    dict_name = "params"

    def __init__(self, value=None, local=False, name=None):
        self.value = value
        self.local = local
        self.name = name
        super().__init__()

    def __set__(self, instance, value):
        dct = getattr(instance, self.__class__.dict_name)
        dct[self.name].value = value

    def __get__(self, instance, owner):
        if instance is not None:
            dct = getattr(instance, self.__class__.dict_name)
        else:
            dct = getattr(owner, self.__class__.dict_name)
        return dct[self.name].value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def evaluated_value(self):
        """ If the parameter's value is an expression, the *evaluated_value* attribute
        stores the result of the evaluation.
        """
        if hasattr(self, '_evaluated_value') and self._evaluated_value is not None:
            return self._evaluated_value
        else:
            return self.value

    @evaluated_value.setter
    def evaluated_value(self, value):
        self._evaluated_value = value

class Float(Parameter):
    pass

