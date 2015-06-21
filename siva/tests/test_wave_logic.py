import pytest
import numpy as np
from ..waveforms.logic import Logic

def test_logic_instance():
    l = Logic(x=np.arange(5)*.1, y=[1,0,0,1,1])

def test_to_ideal_wave():
    l = Logic(x=np.arange(5)*.1, y=[1,0,0,1,1])

    w = l.to_wave()


def test_reduce():

    y = [0, 1, 0, 0, 0, 1, 0, 1, 1, 0]
    x = np.arange(len(y))
    l = Logic(x=x, y=y)

    l2 = l.reduce()

    assert len(l2) == 7

    assert (l2.x == [0, 1, 2, 5, 6, 7, 9]).all()


