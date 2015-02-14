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

    key = '_params'
    store_as = 'value' # Can be 'list', 'dict', or 'value'

    def __init__(self, value, local=False):
        self.value = value
        self.local = local

    @staticmethod
    def _register(self, store_as="attr", dict_name='_params', keyword=None):
        """Stores Parameter in special dictionaries when
        instantiated as part of the class definition.

        This method should be called in __init__ method.
        """
        if not store_as in ('list', 'dict', 'value'):
            raise ValueError("Parameters must be stored as 'list', dict' or 'value'")

        frame = inspect.currentframe()
        c_locals = frame.f_back.f_back.f_locals

        if dict_name not in c_locals:
            c_locals[dict_name] = {}

        if keyword not in c_locals['dict_name']:
            c_locals[dict_name][keyword] = []

        if store_as == "attr":
            c_locals[dict_name][keyword] = self

        elif store_as == "list":
            c_locals[dict_name][keyword].append(self)


    def __set__(self, instance, value):
        instance.params[self.name].value = value

    def __get__(self, instance, owner):
        print("Getting parameter value")
        return instance.params[self.name].value
