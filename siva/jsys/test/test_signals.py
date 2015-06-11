import pytest

from ..signal import Signal



def test_module_declaration():

    class Test():
        s = Signal()

    assert False