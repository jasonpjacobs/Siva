import pytest
from ..signal import Signal

def test_module_declaration():
    class Test():
        s = Signal()

    t = Test()
    t.s = 100
    assert t.s == 100
