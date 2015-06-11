import inspect
from ..components.registered import Registered
from siva.utilities.conversions import float_to_eng

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
    # will be stored in a dictionary named "registry_name"
    registry_name = "params"

    def __init__(self, value=None, local=False, name=None, parent=None, target=None, optional=False, desc=None):
        self.value = value
        self.local = local
        self.name = name
        self.parent = parent
        self.optional = optional
        self.target = target
        self.desc = desc
        super().__init__()

    def __get__(self, instance, owner):
        item = super().__get__(instance, owner)
        return item.value

    def __set__(self, instance, value):
        param = super().__get__(instance, None)
        param.value = value

    def eval(self, globals, locals):
        """Propagates values to the target defined by an expression.  The expression must be defined
        in terms of names contained in the global and local namespaces provided.
        """

        # Handle formula values
        if type(self.value) is str and self.value.startswith('='):
            value = eval(str(self.value), globals, locals)
        else:
            value = self.value
        self.evaluated_value = value

        # The parameter value will be set via exec.  Need to ensure string values are enclosed in quotes.
        if type(value) is str:
            value = "'{}'".format(value)

        # If this variable is a 'remote' variable, set its target
        if self.target is not None:
            # If an non-string iterable wasn't given, wrap it in a list
            if type(self.target) is str:
                targets = [self.target]
            else:
                targets = self.target

            for target in targets:
                try:
                    # Determine if the target expression is a callable.  This may fail
                    # with an attribute error if the target expression is an instance attribute
                    # that hasn't been created yet.

                    evaled_target = eval(target, globals, locals)
                    if callable(evaled_target):
                        exec("{}({})".format(target, value), globals, locals)
                    else:
                        exec("{}={}".format(target, value), globals, locals)
                except AttributeError:
                    # If the target expression is an instance attribute created by evaluating
                    # the expression, the previous eval statement will create an AttributeError
                    # but the expression below will work.
                    exec("{}={}".format(target, value), globals, locals)
                except NameError:
                    raise
                except:
                    error_msg = "Error in parameter evaluation: {}={}".format(target, value)
                    self.parent.error(error_msg)
                    print(error_msg)
                    raise

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

    def __str__(self):
        return str(self.evaluated_value)

    def clone(self, owner=None):
        if owner is None:
            owner = self.parent
        return self.__class__(value=self.value, local=self.local, parent=owner, name=self.name, optional=self.optional,
                              target=self.target, desc=self.desc)

class Float(Parameter):
    def __str__(self):
        return float_to_eng(self.evaluated_value)

class Integer(Parameter):
    def __str__(self):
        return str(self.evaluated_value)

class String(Parameter):
    pass

class File(Parameter):
    pass

class Bool(Parameter):
    pass

