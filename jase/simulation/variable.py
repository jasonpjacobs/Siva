from ..components.parameter import Parameter

class Variable(Parameter):
    def __init__(self, name, target=None, desc=None, local=False, value=None):
        super().__init__(value, local=local)
        self.name = name
        self.target = target
        self.desc = desc
        self.value = value

    def eval(self, globals, locals):
        """Propagates values to the target defined by an expression.  The expression must be defined
        in terms of names contained in the global and local namespaces provided.
        """
        if self.target is not None:
            try:
                # Determine if the target expression is a callable.  This may fail
                # with an attribute error if the target expression is an instance attribute
                # that hasn't been created yet.
                target = eval(self.target, globals, locals)
                if callable(target):
                    exec("{}({})".format(self.target, self.value), globals, locals)
                else:
                    exec("{}={}".format(self.target, self.value), globals, locals)
            except AttributeError:
                # If the target expression is an instance attribute created by evaluating
                # the expression, the previous eval statement will create an AttributeError
                # but the expression below will work.
                exec("{}={}".format(self.target, self.value), globals, locals)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value