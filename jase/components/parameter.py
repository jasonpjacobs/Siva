import inspect

class Parameter:
    """ A class to define Component level attributes.

    Parameter can be declared as pat of a class definition using a declarative syntax:

    class A(Component):
        # Define a parameter named 'b'
        b = Parameter()

    a = A()
    a.b = 2 # Sets the parameter value to 2

    """


    def __init__(self, value=None, local=False, name=None):
        self.value = value
        self.local = local
        self.name = name

    def register(self, parent, dct, name=None):
        """Called by the Component metaclass to add child Components
        to the class's "param" dictionary
        """
        if name is not None:
            self.name = name

        self.parent = parent
        dct["params"][self.name] = self

    def __set__(self, instance, value):
        instance.params[self.name].value = value

    def __get__(self, instance, owner):
        return instance.params[self.name].value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def evaluated_value(self):
        if hasattr(self, '_evaluated_value') and self._evaluated_value is not None:
            return self._evaluated_value
        else:
            return self.value

    @evaluated_value.setter
    def evaluated_value(self, value):
        self._evaluated_value = value
