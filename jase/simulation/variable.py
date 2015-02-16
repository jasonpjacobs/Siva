from ..components.parameter import Parameter

class Variable(Parameter):
    def __init__(self, value=None, name=None, target=None, desc=None, local=False):
        super().__init__(value, local=local)
        self.name = name
        self.target = target
        self.desc = desc
        self.value = value
        self.evaluated_value = None

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
            try:
                # Determine if the target expression is a callable.  This may fail
                # with an attribute error if the target expression is an instance attribute
                # that hasn't been created yet.

                target = eval(self.target, globals, locals)
                if callable(target):
                    exec("{}({})".format(self.target, value), globals, locals)
                else:
                    exec("{}={}".format(self.target, value), globals, locals)
            except AttributeError:
                # If the target expression is an instance attribute created by evaluating
                # the expression, the previous eval statement will create an AttributeError
                # but the expression below will work.
                exec("{}={}".format(self.target, value), globals, locals)
            except NameError:
                raise





