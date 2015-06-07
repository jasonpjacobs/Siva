from collections import UserList
import numpy as np

from .binary import Binary
from .wave import wrap_methods

@wrap_methods
class Pattern(UserList):

    BIN_OPS = ('__add__', '__sub__','__mul__', '__floordiv__','__mod__',
               '__divmod__', '__pow__','__lshift__', '__rshift__', '__and__',
               '__or__', '__xor__', '__truediv__', '__div__',
               '__radd__', '__rsub__', '__rmul__', '__rtruediv__','__rfloordiv__',
                '__rmod__', '__rdivmod__', '__rpow__', '__rlshift__', '__rrshift__',
               '__rand__', '__rxor__', '__ror__',
               '__iadd__', '__isub__', '__imul__', '__itruediv__', '__ifloordiv__',
               '__imod__', '__ipow__', '__ilshift__', '__irshift__', '__iand__', '__ixor__', '__ior__',
               '__lt__', '__le__', '__eq__', '__ne__', '__gt__', '__ge__'
                )

    # Called to implement the built-in functions complex(), int(), float() and round().
    UNARY_WAVE_OPS = ('__neg__', '__neg__',  '__invert__', '__complex__', '__int__', '__float__', '__round__',
                      '__abs__', 'cumsum', 'cumprod')

    # Should return a value of the appropriate type.
    UNARY_VALUE_OPS = ('ptp', 'min', 'max', 'sum', 'mean', 'var', 'std', 'prod',
                       'all', 'any')

    BOOL_BIN_OPS = ('__lt__', '__le__', '__eq__', '__ne__', '__gt__', '__ge__')

    def __init__(self, pattern=None, name=None, repeat=False, width=None):
        """ Creates a pattern given an input Binary item or an integer.

        pattern:  A list of integers, strings or Binary objects
        """
        self.data = []

        self.width = width
        self.name = name
        self.repeat = repeat

        if pattern is not None:
            if isinstance(pattern, str) or isinstance(pattern, Binary):
                self.append(pattern)
            elif hasattr(pattern, '__iter__'):
                for item in pattern:
                    self.append(item)

        # Iteration index
        self._i = 0

    def append(self, item):
        """
        :param item:
        :return:
        """
        self.data.append(Binary(item, width=self.width))

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i == len(self.data) and self.repeat is False:
            raise StopIteration
        value = self.data[self._i % len(self.data)]
        self._i += 1
        return value

    def __getitem__(self, key):
        if self.repeat is False:
            return self.data[key]

        if isinstance(key, slice):
            pass
        elif isinstance(key, int):
            if key >= len(self.data):
                raise IndexError
            else:
                return self.data[key % len(self.data)]

    # ===========================================================
    # Math methods
    # ===========================================================
    def _binary_operation(self, op, other):
        if op in self.BOOL_BIN_OPS:
            if len(self) != len(other):
                return False

            result = np.zeros(len(self), dtype=bool)
            for i, value in enumerate(other):
                method = getattr(self.data[i], op)
                result[i] = method(value)
            return result

        else:
            method = getattr(self.data, op)
            new_y = method(other)
            result = Pattern(new_y)
        return result

    def _unary_wave_operation(self, op):
        results = []
        for value in self.data:
            method = getattr(value, op)
            results.append(method())
        result = Pattern(results, width=self.width)
        return result

    def _unary_value_operation(self, op):
        method = getattr(self.data, op)
        return method()


