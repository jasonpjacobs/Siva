import pytest
import unittest

from ..spice import Tran, Simulation

class Test(Simulation):
    Tran(step=0.2, stop="10n")

def test_something():
    t = Test()


    assert t is not None

    assert len(t.analyses) > 0

    a = t.analyses["tran"]

    assert a.step == 0.2
    assert a.stop == 10e-9