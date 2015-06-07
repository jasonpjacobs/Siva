from .wave import wrap_methods
import numpy as np
import math


def num_of_bits(i):
    # Determine the number of bits required to represent an integer in binary.  Due to the use of log,
    # this is only accurate for low number of bits
    if i > 0:
        w = math.floor(math.log(i,2)) + 1
    else:
        w = math.floor(math.log(abs(i) + 1 ,2)) + 1
        if w ==  math.floor(math.log(abs(i) + 1 ,2)) + 0:
            w -=1
    return w

def int_to_bits(i, width=None, format="twos_complement"):
    """Converts an integer into a list of 1s and 0s of the given width.
    If width is None, it uses the smallest number of bits to represent the number.

    Negative number can either be represented in unsigned, two's complement or sign/magnitude representation.
    Sign-magnitude representation uses a 0 in the MSB to represent a positive number, and a 1 to represent a negative
    number.

    See http://en.wikipedia.org/wiki/Signed_number_representations for a full description.
    """
    if width is not None and not width > 0:
        raise ValueError("Width must be greater than zero. {} was given.".format(width))

    if i == 0:
        if width is not None:
            return [0] * width
        return [0]

    # First figure out the number of bits required to represent this integer.
    w = num_of_bits(i)

    if width is None:
        width = w
    # Then, if the number is negative, calculate its two's value complement
    if i < 1 and format == "twos_complement":
        v = (1<<width) + i
    elif i > 1 and format == "sign_magnitude":
        v = 2**(width + 1) + i
    else:
        v = i

    # Find the bit value for each column
    bits = []
    while v:
        if v & 1 == 1:
            bits.append(1)
        else:
            bits.append(0)
        v >>= 1

    # If width is specified pad the bits
    if width is not None and len(bits) < width:
        if i > 0:
            bits = bits + [0]*(width - len(bits))
        else:
            bits = bits + [1]*(width - len(bits))

    return bits[::-1]

def bits_to_int(b, format="unsigned"):
    """
    :param b: A representation of a binary number as a list of 1's and 0's
    :param format: The signed number representation format:  unsigned, twos_complement, or sign_magnitude
    :return: The corresponding integer representation
    """
    if format == "unsigned":
        sign = 1
        mag = b
    elif format == "sign_magnitude":
        sign = -1 if b[0] == 1 else 0
        mag = b[1:]
    elif format == "twos_complement":
        sign = -1 if b[0] == 1 else 0
        mag = b[1:]
    else:
        raise ValueError("format must be 'unsigned', 'twos_complement', or 'sign_magnitude'")

    # Convert magnitude to integer, then correct for sign and/or two's complement shift
    v = 0
    for i, bit in enumerate(mag):
        v += 2**((len(mag) - 1)-i)*bit

    if format == "twos_complement":
        integer = sign*(2**(len(mag)) - v)
    else:
        integer = sign*v
    return integer


@wrap_methods
class Binary():

    BIN_OPS = ('__add__', '__sub__','__mul__', '__floordiv__','__mod__',
               '__divmod__', '__pow__','__lshift__', '__rshift__', '__and__',
               '__or__', '__xor__', '__truediv__', '__div__',
               '__radd__', '__rsub__', '__rmul__', '__rtruediv__','__rfloordiv__',
                '__rmod__', '__rdivmod__', '__rpow__', '__rlshift__', '__rrshift__',
               '__rand__', '__rxor__', '__ror__',
               '__iadd__', '__isub__', '__imul__', '__itruediv__', '__ifloordiv__',
               '__imod__', '__ipow__', '__ilshift__', '__irshift__', '__iand__', '__ixor__', '__ior__',
               '__lt__', '__le__', '__eq__', '__ne__', '__gt__', '__ge__',
                )

    INPLACE_OPS =     ('__iadd__', '__isub__', '__imul__', '__itruediv__', '__ifloordiv__',
               '__imod__', '__ipow__', '__ilshift__', '__irshift__', '__iand__', '__ixor__', '__ior__')

    BOOL_OPS = ('__lt__', '__le__', '__eq__', '__ne__', '__gt__', '__ge__')

    # Called to implement the built-in functions int(), float() and round().
    UNARY_WAVE_OPS = ('__neg__', '__complex__', '__float__', '__round__',
                      '__abs__', 'cumsum', 'cumprod')

    # Note:  '__invert__' is handled separately
    UNARY_VALUE_OPS = ()

    def __init__(self, value, width=None, signed=False):
        self.width = width
        self.signed = signed

        if not signed:
            if value < 0:
                value = abs(value)

        if width is None:
            self.value = value
        else:
            bits = int_to_bits(int(value), width)
            if len(bits) > width:
                # Truncate to the last *width* bits
                v = bits_to_int(bits[-(width):])
            else:
                v = bits_to_int(bits)

            self.value = v

    def _unary_wave_operation(self, op):
        method = getattr(self.value, op)
        value = method()
        return Binary(value, width=self.width)

    def _unary_value_operation(self, op):
        method = getattr(int, op)
        return method()

    def _binary_operation(self, op, other):
        if type(other) is Binary:
            other = int(other)
        if op in self.INPLACE_OPS:
            # '__iadd__' --> '__add__'
            new_op = op.replace('__i','__')
            method = getattr(self.value, new_op)
            result = method(other)
            self.value = result
        elif op in self.BOOL_OPS:
            method = getattr(self.value, op)
            return method(other)
        else:
            method = getattr(int, op)
            result = method(int(self), other)
        return Binary(result, width=self.width)

    #def __eq__(self, other):
    #    return int(self) == int(other)

    def __int__(self):
        # The logic value is stored as an integer.  Python integers are normally
        # stored in sign/magnitude format.  If the logic value is unsigned we need translate
        # the integer value.
        if self.signed:
            return self.value & (2**len(self))
        else:
            return int(self.value)

    def __len__(self):
        if self.width is None:
            return num_of_bits(self.value)
        else:
            return self.width

    def __invert__(self):
        return Binary(~self.value & 2**(len(self))-1, width=self.width)

    @property
    def bits(self):
        return int_to_bits(self.value, self.width)

    def __getitem__(self, key):
        """ Slices the logic value according to Verilog bit selection rules.

        These are different than normal Python based slicing.
        1. The individual bits are indexed from the MSB down to the LSB.  E.g., value[6:3] is 6 down to 3
        2. Python slices consist of a start/stop/step combo, but the stop value is NOT included in the range.
            This isn't the case for Verilog.  bus[3:0]

        """
        if isinstance(key, slice):
            step  = key.step if key.step is not None else 1

            if key.start and key.stop:
                if key.start > key.stop:
                    downto = True
                else:
                    downto = False
            elif key.start or key.stop:
                downto = True
            elif key.step > 0:
                downto = False
            else:
                downto = True

            # MSB down to LSB
            if downto:
                step = -1*abs(step)
                start = key.start if key.start else len(self) - 1
                stop  = key.stop - 1 if key.stop else -1
                bits = self.bits[::-1]
            else:
                start = key.start if key.start else 0
                stop = key.stop + 1 if key.stop else len(self)
                bits = self.bits

            slices = [bits[i] for i in range(start, stop ,step)]
            return Binary(bits_to_int(slices))
        else:
            if key < len(self):
                return self.bits[key]
            else:
                if self.width and key >= self.width:
                    raise IndexError()
                else:
                    if self.signed:
                        return 1 if self.value < 0 else 0
                    else:
                        return 0


    def __repr__(self):
        return "Binary({})".format(int(self.value))
