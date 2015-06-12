import pytest

from siva.waveforms.wave import Wave
from siva.waveforms.clock import ClockSource

import numpy as np

def test_clock_source():
    clk = ClockSource(period=.1, phase=.02, duty=0.5)
    crossings = clk.ticks(n=4)
    np.testing.assert_allclose(crossings, [.02, .12, .22, .32])

    clk = ClockSource(frequency=10, phase=.02, duty=0.5)
    crossings = clk.ticks(n=4)
    np.testing.assert_allclose(crossings, [.02, .12, .22, .32])

    with pytest.raises(ValueError):
        clk = ClockSource()

    clk = ClockSource(period=.1, phase=.02, duty=0.5)
    with pytest.raises(ValueError):
        ticks = clk.ticks()

    with pytest.raises(ValueError):
        ticks = clk.ticks(edge="RISE", n=10)


def test_clock_source_stop():

    clk = ClockSource(period=0.5, stop=4.2, phase=.1)

    ticks = clk.ticks()
    np.testing.assert_allclose(ticks, [ 0.1,  0.6,  1.1,  1.6,  2.1,  2.6,  3.1,  3.6,  4.1])

    ticks = clk.ticks(edge='falling')
    np.testing.assert_allclose(ticks, [ 0.35,  0.85,  1.35,  1.85,  2.35,  2.85,  3.35,  3.85])

def test_jitter():
    clk = ClockSource(period=0.5, stop=4.2, phase=.1)

    jitter = clk.jitter()

    # Should be zero (less than the machine's accuraccy for floats
    assert jitter.y.sum() < np.finfo(float).eps*len(jitter.y)




