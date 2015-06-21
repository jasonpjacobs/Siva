import numpy as np
from ..waveforms import Wave

class ClockBase:
    """ A mixin class for adding clock like behavior to a waveform.

    """

    def ticks(self):
        """Returns the first n ticks of the clock.
        """
        raise NotImplementedError

    def periods(self):
        ticks = self.ticks()
        periods = np.diff(ticks)
        x = np.array(ticks)
        y = periods
        np.append(y, y[-1])
        name = "Periods({})".format(self.name)
        w = Wave(name=name, x=x, y=y)
        return w

    def phase(self):
        """Returns the phase of this clock as a waveform.  The Y values of the waveform
        represent the number of cycles elapsed.  The x values are the time when that cycle has
        completed.
        """
        x = self.ticks()
        y = np.range(len(x))
        name = "Phase({})".format(self.name)
        w = Wave(name=name, x=x, y=y)
        return w

    def jitter(self, ideal=None, n=None, edge="rising", type="period", n_cycles=1):
        """ Calculates different types of clock jitter.

        period:  Period jitter is measured as the difference between a given clock period and the ideal period.

        cycle: (Cycle-cycle jitter) is measured as the difference between two adjacent periods

        tie:  (Time interval error):  Measures the time difference between an edge of the jittered
        clock and the corresponding edge of the ideal clock.

        """

        # Get a list of all the clock crossings
        ticks = self.ticks(edge=edge)

        periods = np.diff(ticks)

        if ideal is None:
            ideal = np.average(periods)

        if type == "period":
            x = np.array(ticks)

            y = periods - ideal

            # y[n] represents the period between x[n] and x[n+1].
            # Repeat the last yvalue so the x and y vectors have the same length
            np.append(y, y[-1])

            name = "Period Jitter({})".format(self.name)
        elif type == "cycle":
            raise NotImplementedError("Cycle cycle jitter is not implemented")
        elif type == "tie":
            raise NotImplementedError("Time Interval Error jitter is not implemented")
        else:
            raise ValueError("Jitter type uknown: {}".format(type))

        w = Wave(name=name, x=x, y=y)

        return w

class ClockSource(ClockBase):
    def __init__(self, period=None, frequency=None, phase=0, duty=0.5, stop=None, name=None):
        """
        Base class for clock sources, used to define stimulus for simulations.

        :param period: Period of the ideal clock, in seconds.
        :param frequency: Frequency of the ideal clock, in Hertz
        :param phase:  Phase of the ideal clock, in seconds.
        :param duty: Duty cycle of the clock, Ratio of the high period to the low period
        :param stop:  Defines the stop time for a fixed duration clock.  Clocks with
        finite durations can implement the jitter, periods methods.
        :return:
        """
        if period is None and frequency is None:
            raise(ValueError("Either period or frequency must be defined"))

        if frequency:
            period = 1/frequency

        self.period = period
        self.phase = phase

        assert 0 < duty < 1.0
        self.duty = duty

        self.stop = stop

        if name is None:
            name = "Clk"
        self.name = name

    def ticks(self, n=None, edge='rising'):
        if n is None and self.stop is None:
            raise ValueError("Need to provide number of desired clock ticks")

        if n is None:
            n_rise = int((self.stop-self.phase)/self.period) + 1
            n_fall = int((self.stop-self.phase-self.period*0.5)/self.period) + 1
        else:
            n_rise = n
            n_fall = n

        ticks = []
        if edge == 'rising' or edge == 'both':
            ticks.extend([self.phase + i*self.period for i in range(n_rise)])
        elif edge == 'falling' or edge == 'both':
            assert self.duty is not None
            ticks.extend([self.phase + i*self.period + self.period*self.duty for i in range(n_fall)])
        else:
            raise ValueError("Edge type must be 'rising', 'falling', or 'both")

        if n is not None:
            ticks = [ticks[i] for i in range(n)]

        return ticks


