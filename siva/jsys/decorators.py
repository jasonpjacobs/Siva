
import inspect
import pdb
import types

from functools import wraps
from .signal import Signal

class triggerable:
    def __init__(self, *args):
        self.args = args

    def __call__(self, func):

        code = func.__code__
        vars = code.co_names

        @wraps(func)
        def wrapper(self):
            func(self)
        return wrapper


    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return types.MethodType(self, instance)

class event(triggerable):
    def __call__(self, func):
        # Put our function on the call back list of
        for arg in self.args:
            if isinstance(arg, Signal):
                arg._callbacks.append(func)

        return super().__call__(func)
