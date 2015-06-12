import pytest
import unittest

from siva.waveforms.pattern import Pattern


def test_creation():
    p = Pattern(name='test', repeat=True)


def test_iteration():

    p = Pattern([0,1,2,3,4])

    results = []
    for i in p:
        results.append(i)

    assert results == [0, 1, 2, 3, 4]

    p = Pattern([0,1,2,3,4], repeat=True)
    results = []

    i = 0
    for pat in p:
        if i == 10:
            break
        results.append(pat)
        i += 1

    assert results == [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]


def test_selection():
    p = Pattern([0, 1, 2, 3, 4])
    assert p[0] == 0
    assert p[1] == 1
    assert p[2] == 2
    assert p[3] == 3
    assert p[4] == 4

    with pytest.raises(IndexError):
        p[5]

    assert p[-5] == 0
    assert p[-4] == 1
    assert p[-3] == 2
    assert p[-2] == 3
    assert p[-1] == 4

    assert p[0:2] == [0,1]
    assert p[3:] == [3,4]
    assert p[0::2] == [0, 2, 4]
    assert p[::-1] == [4, 3, 2, 1, 0]


def test_concatenation():

    p = Pattern()

    for i in range(5):
        p = p + [i]

    result = list(p)
    assert result == [0, 1, 2, 3, 4]

def test_multiplication():
    p = Pattern([0,1])
    assert (p*3 == [0,1,0,1,0,1]).all()


def test_logic():

    p = Pattern([0b00, 0b11], width=2)

    assert (p == [0b00, 0b11]).all()

    assert (~p == [0b11, 0b00]).all()

