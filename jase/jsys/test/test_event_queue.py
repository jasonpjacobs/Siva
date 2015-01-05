import pytest

from ..event_queue import EventQueue
from ..event import Event

@pytest.fixture
def event_queue():
    return EventQueue()

def test_empty(event_queue):
    assert event_queue.empty

@pytest.fixture
def test_put(event_queue):

    eq = EventQueue()

    assert(eq.empty)

    for i in range(10):
        eq.put(Event(i))
        assert( len(eq) == 2*i + 1)

        eq.put(Event(i*10))
        assert( len(eq) == 2*(i+1))

    assert( len(eq) == 20)
    return eq

def test_get(test_put):
    eq = EventQueue()
    for i in range(10):
        eq.put(Event(i))
        eq.put(Event(i*10))

    assert len(eq) == 20

    event = eq.get()
    assert event.time == 0
    assert eq.heap[0].time == 0

    for i in range(11):
        print(i, event.time)
        event = eq.get()
        assert event.time == i

    for i in range(2,9):
        print(i, event.time)
        event = eq.get()
        assert event.time == i*10


