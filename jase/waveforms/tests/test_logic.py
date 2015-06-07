import pytest
from jase.waveforms.binary import Binary, int_to_bits, bits_to_int


"""
'__add__', '__sub__','__mul__', '__floordiv__','__mod__',
               '__divmod__', '__pow__','__lshift__', '__rshift__', '__and__',
               '__or__', '__xor__', '__truediv__', '__div__',
               '__radd__', '__rsub__', '__rmul__', '__rtruediv__','__rfloordiv__',
                '__rmod__', '__rdivmod__', '__rpow__', '__rlshift__', '__rrshift__',
               '__rand__', '__rxor__', '__ror__',
               '__iadd__', '__isub__', '__imul__', '__itruediv__', '__ifloordiv__',
               '__imod__', '__ipow__', '__ilshift__', '__irshift__', '__iand__', '__ixor__', '__ior__',
               '__lt__', '__le__', '__eq__', '__ne__', '__gt__', '__ge__'

"""

def test_bits():
    """
    Bits	Unsigned value	2's complement value
    011	3   3
    010	2   2
    001	1   1
    000	0   0
    111	7   -1?
    110	6   -2?
    101	5   -3?
    100	4   -4?
    """
    assert int_to_bits(3) == [1, 1]
    assert int_to_bits(2) == [1, 0]
    assert int_to_bits(1) == [1]
    assert int_to_bits(0) == [0]
    assert int_to_bits(-1) == [1, 1]
    assert int_to_bits(-2) == [1, 0]
    assert int_to_bits(-3) == [1, 0, 1]
    assert int_to_bits(-4) == [1, 0, 0]


    assert int_to_bits(3, width=3) == [0, 1, 1]
    assert int_to_bits(2, width=3) == [0, 1, 0]
    assert int_to_bits(1, width=3) == [0, 0, 1]
    assert int_to_bits(0, width=3) == [0, 0, 0]
    assert int_to_bits(-1, width=3) == [1, 1, 1]
    assert int_to_bits(-2, width=3) == [1, 1, 0]
    assert int_to_bits(-3, width=3) == [1, 0, 1]
    assert int_to_bits(-4, width=3) == [1, 0, 0]

    with pytest.raises(ValueError):
        int_to_bits(10, width=0)


def test_bits_to_int():

    assert bits_to_int([0]) == 0
    assert bits_to_int([1]) == 1

    assert bits_to_int([0, 0]) == 0
    assert bits_to_int([1, 0]) == 2
    assert bits_to_int([1, 1]) == 3

    # Need to test "sign_magnitude" and "twos_complement" representations

def test_logic_instance():

    n = Binary(0b101)
    assert n == 5

    n += 1
    assert n == 6

    a = Binary(0b1)
    assert ~a == 0


def test_len():
    assert len(Binary(0b0)) == 1
    assert len(Binary(0b1)) == 1

    assert len(Binary(0b00)) == 1
    assert len(Binary(0b11)) == 2


    assert len(Binary(0b0, width=4)) == 4
    assert len(Binary(0b1, width=4)) == 4



def test_casting():

    assert int(Binary(0b0)) == 0
    assert int(Binary(0b1)) == 1

    assert int(Binary(-1)) == 1
    assert int(Binary(-1, width=10)) == 1



def test_truncation():

    assert Binary(0b1100, width=2) == 0
    assert Binary(0b1101, width=2) == 1

    assert Binary(0b1111, width=10) == Binary(15)


def test_int():
    assert int(Binary(0b1) == 1)
    assert int(Binary(0b11) == 3)

    assert int(Binary(-2, signed=False) == 2)


    assert int(Binary(-2, signed=True) == -2)


def test_logic_methods():

    assert Binary(0b1) << 2 == Binary(0b100)
    assert Binary(0b1000) >> 2 == Binary(0b10)

    # And/or/nand/nor
    assert Binary(0b1000) & Binary(0b001) == Binary(0b0000)
    assert Binary(0b1000) | Binary(0b001) == Binary(0b1001)

    # XOR
    assert Binary(0b1001) ^ Binary(0b0110) == Binary(0b1111)


    # Inversion
    assert ~Binary(0b1001) == Binary(0b0110)
    assert ~Binary(0b0000) == Binary(1)


def test_logic_bit_select():

    assert Binary(0b0001)[0] == 1

    assert Binary(0b0001)[3] == 0

    # Unsized logic will just sign extend
    assert Binary(0b0001)[4] == 0

    assert Binary(-3, signed=True)[100] == 1

    # Sized logic values should raise an index error
    with pytest.raises(IndexError):
        Binary(0b0001, width=4)[4]

    with pytest.raises(IndexError):
        Binary(-3, signed=True, width=4)[4]


    assert Binary(0b001100)[3:] == Binary(0b1100)
    assert Binary(0b001100)[3:2] == Binary(0b11)


    assert Binary(0b10001011)[3:0] == Binary(0b1011)
    assert Binary(0b10001011)[3:]  == Binary(0b1011)
    assert Binary(0b10001011)[:1]  == Binary(0b1000101)
    assert Binary(0b10001011)[7:4]  == Binary(0b1000)

    assert Binary(0b10101010)[7:4:2] == Binary(0b11)
    assert Binary(0b10101010)[7::2] == Binary(0b1111)


    # assert Logic(0b10101010)[:0:2] == Logic(0b0000)
