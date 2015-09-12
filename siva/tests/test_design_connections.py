import pytest


from siva.design.interface import Bus
from siva.design.connections import Net, Pin, convert_slice

def test_empty_net():
    a = Net(name='a')

    assert a.name == 'a'

def test_wire_connect():

    o1 = Pin("out")
    i1 = Pin("in")

    n1 = Net("n1")

    o1.connect(n1)
    i1.connect(n1)

    assert len(n1.ports) == 2
    assert set(n1.ports) == set([o1, i1])


def test_convert_slice():
    s = convert_slice(slice(0,5))
    assert list(range(s.start, s.stop, s.step)) == [0,1,2,3,4,5]

    s = convert_slice(slice(5,0))
    assert list(range(s.start, s.stop, s.step)) == [5,4,3,2,1,0]

    s = convert_slice(slice(0,5, 2))
    assert list(range(s.start, s.stop, s.step)) == [0, 2, 4]

    s = convert_slice(slice(5,0, 2))
    assert list(range(s.start, s.stop, s.step)) == [5, 3, 1]


    s = convert_slice(slice(0,5), max=4)
    assert list(range(s.start, s.stop, s.step)) == [0, 1, 2, 3, 4]

    s = convert_slice(slice(0,5), min=2)
    #assert list(range(s.start, s.stop, s.step)) == [2, 3, 4]

    s = convert_slice(slice(5,0), min=2)
    assert list(range(s.start, s.stop, s.step)) == [5, 4, 3, 2]

    s = convert_slice(slice(5,0), max=3)
    assert list(range(s.start, s.stop, s.step)) == [3, 2, 1, 0]

def test_bus_net():
    b = Net(name="bus", width=4)

    assert str(b[0]) == "bus[0]"

    assert str(b[1:0]) == "bus[1:0]"

    #assert False

