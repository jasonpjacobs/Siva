"""


TODO:  Create a wave class whose y-values correspond to an pair of x values.
    - E.g., a waveform of clock periods would have y[n] represent the period between the time at x[n] and x[n+1]
    - Used for the output of discrete differences, histograms, etc.

"""
import numpy as np
import collections

Point = collections.namedtuple('Point', ['x', 'y'])

def wrap_binary_op_method(cls, op):
    def wrapped(self, other):
        return self._binary_operation(op, other)
    return wrapped

def wrap_unary_wave_op_method(cls, op):
    def wrapped(self):
        #return self._unary_operation(op)
        try:
            return self._unary_wave_operation(op)
        except:
            raise
    return wrapped

def wrap_unary_value_op_method(cls, op):
    def wrapped(self):
        return self._unary_value_operation(op)
    return wrapped

def wrap_methods(cls):
    """
    :param cls:
    :return:
    """
    for op in cls.BIN_OPS:
        setattr(cls, op, wrap_binary_op_method(cls, op))

    for op in cls.UNARY_WAVE_OPS:
        setattr(cls, op, wrap_unary_wave_op_method(cls, op))

    for op in cls.UNARY_VALUE_OPS:
        setattr(cls, op, wrap_unary_value_op_method(cls, op))
    return cls


@wrap_methods
class Wave:
    """ A waveforms (waveform) is an 2D data structure containing x and y vectors.  The x,y pairs may be ordered or unordered.

    """
    BIN_OPS = ('__add__', '__sub__','__mul__', '__floordiv__','__mod__',
               '__divmod__', '__pow__','__lshift__', '__rshift__', '__and__',
               '__or__', '__xor__', '__truediv__', '__div__',
               '__radd__', '__rsub__', '__rmul__', '__rtruediv__','__rfloordiv__',
                '__rmod__', '__rdivmod__', '__rpow__', '__rlshift__', '__rrshift__',
               '__rand__', '__rxor__', '__ror__',
               '__iadd__', '__isub__', '__imul__', '__itruediv__', '__ifloordiv__',
               '__imod__', '__ipow__', '__ilshift__', '__irshift__', '__iand__', '__ixor__', '__ior__',
               '__lt__', '__le__', '__eq__', '__ne__', '__gt__', '__ge__'
                )

    # Called to implement the built-in functions complex(), int(), float() and round().
    UNARY_WAVE_OPS = ('__neg__', '__neg__',  '__invert__', '__complex__', '__int__', '__float__', '__round__',
                      '__abs__', 'cumsum', 'cumprod')

    # Should return a value of the appropriate type.
    UNARY_VALUE_OPS = ('ptp', 'min', 'max', 'sum', 'mean', 'var', 'std', 'prod',
                       'all', 'any')

    def __init__(self,data=None, x=None, y=None, name=None, desc=None, interp='linear', default=None,
                 threshold=None):
        self.name = name
        self.desc = desc
        self.interp = interp
        self.default = default

        self._x = []
        self._y = []
        self.build_mode = False
        self._build_mode = False

        if data is None and x is None and y is None:
            # Create an empty Wave that can be built incrementally
            # (via simulation, for example)
            self.build_mode = True
        else:
            self._parse_inputs(data, x, y)

        self.threshold = threshold

    def _parse_inputs(self, data, x, y):
        if data is not None and x is None and y is None:
            # If data is a sequence with elements of length 1, assume
            # that no X is given, and create one
            if len(data) > 0 and not isinstance(data[0], collections.Iterable):
                x = np.arange(len(data))
                y = data
            # If all the elements of the data vector are length two,
            # assume data is a list of (x,y) pairs.
            elif np.array([len(v) == 2 for v in data]).all():
                x = [v[0] for v in data]
                y = [v[1] for v in data]
            # Check if two X, Y lists were passed as arguments
            elif len(data) == 2 and len(data[0]) != 2:
                x = data[0]
                y = data[1]
        elif data is not None and x is not None and y is None:
            y = x
            x = data
        elif x is not None and y is not None:
            x = x
            y = y
        elif y is not None and x is None:
            x = np.arange(len(y))
            y = y
        else:
            raise(ValueError)

        # Convert to Arrays
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(y, np.ndarray):
            y = np.array(y)

        self.x, self.y = x, y

    def __repr__(self):
        txt = []
        txt.append("{}([".format(str(self.__class__.__name__)))
        for p in self.points:
            txt.append("    [{}, {}]".format(repr(p[0]), repr(p[1])))
        txt.append('    ], name="{}")'.format(self.name))
        return "\n".join(txt)

    @property
    def x(self):
        if self._build_mode:
            if len(self._x):
                return self._x[-1]
            else:
                return 0
        return self._x

    @x.setter
    def x(self, value):
        if self._build_mode:
            return self._x.append(value)
        if isinstance(value, Wave):
            self._x = value
        else:
            self._x = np.array(value)
        self._x_changed()

    def _x_changed(self):
        # Recompute the sample rate and order
        dx = np.diff(self.x)
        if len(dx) > 0 and dx.ptp() < len(self.x)*np.finfo(float).eps:
            self.dx = dx[0]
            if dx[0] > 0:
                self.order = 'ascending'
            else:
                self.order = 'descending'
        else:
            self.dx = None
            self.order = None

    @property
    def y(self):
        if self.build_mode:
            if len(self._y):
                return self._y[-1]
            else:
                return 0

        return self._y

    @y.setter
    def y(self, value):
        if self._build_mode:
            return self._x.append(value)
        if isinstance(value, Wave):
            self._y = value
        else:
            self._y = np.array(value)

    def append(self, x,y):
        if self.build_mode:
            self._x.append(x)
            self._y.append(y)
        else:
            np.append(self._x, x)
            np.append(self._y, y)

    @property
    def build_mode(self):
        return self._build_mode

    @build_mode.setter
    def build_mode(self, value):
        if value:
            # Convert x, y arrays to Python lists
            self._x = self._x.tolist()
            self._y = self._y.tolist()
        else:
            self._x = np.array(self._x)
            self._y = np.array(self._y)
        self._build_mode = value

    @property
    def points(self):
        return np.dstack((self.x,self.y))[0]

    @points.setter
    def points(self, points):
        self.x = points[:,0]
        self.y = points[:,1]

    def __len__(self):
        return self.x.__len__()

    def _binary_operation(self, op, other):
        if self._build_mode:
            return getattr(self.y, op)(other)

        if isinstance(other, Wave):
            # If the domains are the same, operate on the y arrays only.
            if len(self.x) == len(other.x) and (self.x == other.x).all():
                x = self.x
                y = np.copy(other.y)
            # Otherwise, combine the domains and interpolate
            else:
                # Find a common domain, interpolate
                # and perform the operation
                # print(self.x, other.x)
                raise(NotImplementedError)
        else:
            x = self.x
            y = other

        method = getattr(self.y, op)
        new_y = method(y)
        result = Wave(x=x, y=new_y)
        return result

    def _unary_wave_operation(self, op):
        method = getattr(self.y, op)
        new_y = method()
        result = Wave(x=self.x, y=new_y)
        return result

    def _unary_value_operation(self, op):
        method = getattr(self.y, op)
        return method()

    def __getitem__(self, key):
        # Wave[0]
        if isinstance(key, int):
            return Point(self.x[key], self.y[key])
        else:
            return Wave(x=self.x[key], y=self.y[key])

    def __call__(self, values,  kind=None, bounds_error=False ):
        return self.interpolate(values, kind, bounds_error)

    def clip(self, *args, **kwargs):
        return Wave(x=self.x,  y=self.y.clip(*args, **kwargs))

    def convolve(self, other, mode="full"):
        if isinstance(other, collections.Iterable):
            other = np.array(other)

        # Find
        if self.dx is not None:
            a_dx = self.dx
        else:
            a_dx = np.diff(self.x).min()

        if isinstance(other, np.ndarray):
            other = Wave(x=np.linspace(0, len(y)*a_dx, len(y), True), y=other)
        elif isinstance(other, Wave):
            pass
        else:
            print(type(other))
            raise ValueError("Argument to convolve must be a Wave, numpy array or a sequence")

        if other.dx is None:
            b_dx = np.diff(other.x).min()
        else:
            b_dx = other.dx

        # Resample both waveforms to a common domain
        if a_dx < b_dx:
            a = self
            b = other.sample(a_dx)
        elif a_dx > b_dx:
            a = self.sample(b_dx)
            b = other
        elif a_dx == b_dx:
            a = self
            b = other

        if a.dx is None:
            pdb.set_trace()
        # Perform the convolution
        y = np.convolve(a.y, b.y, mode=mode)
        x = np.linspace(self.x[0], len(y)*a.dx, len(y))
        pdb.set_trace()
        return Wave(x=x, y=y)

    def cross(self, value, edge="either"):
        """ Returns an array of values where the waveform crosses the given y-value.

        :param value: Y-value that waveform crosses
        :param edge:  Type of waveform crossing.  Should be "either", "rising" or "falling"
        :return: An array of x-values where the waveform has crossed the given y-value
        """
        assert(edge in ("either", "rising", "falling", "both"))
        w = self.y - value

        # Find out where two adjacent samples change signs
        signs = w[:-1]*w[1:]
        cross_indices = signs <= 0

        # Get the difference function (derivative)
        # to determine cross types

        dy = np.diff(self.y)

        # Now finding the crossings
        if edge == "either" or edge == "both":
            i = cross_indices
        elif edge == "rising":
            i = cross_indices & (dy >= 0)
        elif edge == "falling":
            i = cross_indices & (dy <= 0)

        # Interpolate if needed to find the exact
        # x values
        if self.interp in ('nearest',):
            # Choose half way between crossing points
            x = (self.x[i] + self.x[i+1])/2
        elif self.interp in ('zero', 'step'):
            # Choose X[i]
            x = self.x[i]
        elif self.interp in ('linear', 'slinear', None):
            # Interpolate linear between indices
            dx = np.diff(self.x)
            x = self.x[i] + dx[i]*abs(w[i]/(dy[i]))
            x = x[~np.isnan(x)]
        else:
            raise(NotImplementedError, "Cubic, spline interpolation not implemented")
        return x

    def cumsum(self):
        """Returns the cumulative sum of the y-axis"""
        return Wave(x=self.x, y=np.cumsum(self.y))

    def derivative(self):
        y = np.diff(self.y)/np.diff(self.x)
        return Wave(x=self.x[:-1], y=y, name = "dx/dy({})".format(self.name))

    def difference(self):
        """Returns the first difference of the waveform's y-axis values"""
        return Wave(x=self.x[:-1], y=np.diff(self.y))

    def fft(self):
        x = np.fft.fftfreq(len(self.x), self.dx)
        y = np.fft.fft(self.y)

        idx = x.argsort()
        x = x[idx]
        y = y[idx]
        return Wave(x=x,y=y)

    def flip(self, axis="x"):
        """ Inverts the waveform about the specified axis.

        :return:
        """
        assert(axis in ("x", "y"))
        if axis == "x":
            self.x = self.x[::-1]
        if axis == "y":
            self.y = self.y[::-1]

    def ifft(self):
        """The input should be ordered in the same way as is returned by fft, i.e.,
        a[0] should contain the zero frequency term, a[1:n/2+1] should contain the positive-frequency terms,
        and a[n/2+1:] should contain the negative-frequency terms, in order of decreasingly negative frequency.
        See numpy.fft for details.
        """
        y=self.y
        x=self.x
        if self.order == "ascending":
            # This means the frequency bins have been sorted.  Need to reorder the y-values
            # to match the order expected by np.fft.ifft:
            # "a[0] should contain the zero frequency term, a[1:n/2+1] should contain
            # the positive-frequency terms,  and a[n/2+1:] should contain the negative-frequency terms"

            if (min(x)) >=0:
                freqs = x
                pos_ndx = freqs > 0
                pos_freqs = freqs[pos_ndx]
                pos_freq_values = self.y[pos_ndx]

                x = np.append(-1*pos_freqs[::-1], x)
                y = np.append(pos_freq_values[::-1], y)

                # The frequency spectrum is positive

            y = np.fft.ifftshift(self.y)
        else:
            y = self.y

        y = np.fft.ifft(y)

        N = len(y) - 1
        df = np.diff(x)[0]
        T = 1/df
        dt = T/(len(y))
        x = np.linspace(0,N*dt,N+1, True)
        return Wave(x=x, y=y)

    def integral(self, start=None, end=None, method="trapz"):
        """ Returns a waveform of the approximated area between
        samples, using the specified integration method.

        To get a definite integral, use the *integerate* method.
        """
        assert(method in ("trapz", "rect", "forward", "backward"))

        if start is not None or end is not None:
            w = self.slip(start=start, end=end)
        else:
            w = self
        from scipy import integrate
        if method == "trapz":
            dx = np.diff(self.x)
            dy = np.diff(self.y)
            y = dx*(self.y[:-1] + dy)/2
            y = np.cumsum(self.y)[:-1]*dx
            y = integrate.cumtrapz(self.y, self.x)
            #y = np.trapz(self.y, self.x)
        elif method == "forward":
            dx = np.diff(self.x)
            y = 0*self.y[:-1] + self.y[:-1] * dx
        elif method == "backward":
            dx = np.diff(self.x)
            y = 0*self.y[:-1] + self.y[1:] * dx

        return Wave(x=self.x[:-1], y=y, name="Int({})".format(self.name), interp=self.interp)

    def integrate(self, start=None, end=None, method="trapz"):
        """ Computes the definite integral of the waveform
        using the specified integration method.
        """
        assert(method in ("trapz", "rect", "forward", "backward"))
        integral = self.integrate(start=start, end=end)
        return integral.sum()

    @property
    def interp(self):
        """ Property describing the default type of interpolation to perform.
        """
        return self._interp

    @interp.setter
    def interp(self, value):
        assert( value in ('linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'step'))
        self._interp = value

    def interpolate(self, values, kind=None, bounds_error=False):
        import scipy
        from scipy import interpolate

        if kind is None:
            kind = self.interp

        assert( kind in ('linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'step'))
        # Alias 'step' with 'zero'
        if (kind == "step"):
            kind = 'zero'

        kind_order = {'linear' : 1,
                      'zero' : 0,
                      'slinear' : 0,
                      'quadratic' : 2,
                      'cubic': 3,
                      'step': 0
                      }

        if kind == 'zero':
            f = interpolate.interp1d(self.x,self.y, kind='zero', bounds_error=bounds_error)
        else:
            # Using Univariate Spline gives us extrapolation too
            f = interpolate.InterpolatedUnivariateSpline(self.x, self.y, k=kind_order[kind])

        # Convert lists and numbers into ndarrays
        if not isinstance(values, np.ndarray):
            # Int, float, bool, etc.
            if not isinstance(values, collections.Iterable):
                values = (values,)
            values = np.array(values)

        y = f(values)
        w = self.__class__(x=values, y=y)
        return w

    def irfft(self):
        y = np.fft.irfft(self.y)
        dt = 0.5/self.x[-1]
        T = 2*(len(self.y) - 1)*dt
        x = np.arange(0, T, dt)
        return Wave(x=x, y=y)

    def rfft(self):
        x = np.fft.rfftfreq(len(w.x), w.dx)
        y = np.fft.rfft(w.y)
        return Wave(x=x,y=y)

    def sample(self, clock=None, period=None, freq=None, start=None):
        """ Samples the waveform using a givek clock signal, or
        by specifying a period or frequency.

        :param clock: A Wave that implements the clock protocol (ticks)
        :param period: Sample period, in seconds.
        :param freq:  Sample frequency, in Hertz
        :param start: Start time for the sampling.
        :return:
        """
        if period is None and freq is None and clock is None:
            raise(TypeError, "Either period or frequency should be provided.")
        elif period is not None and freq is not None:
            raise(TypeError, "Either period or frequency should be provided, not both.")
        else:
            if freq is not None:
                period = 1/freq

        if start is None:
            start = self.x[0]

        if not clock:
            # arange does not include the stop point,
            # so add a half step to ensure it is included
            stop = self.x[-1] + period/2
            x = np.arange(start, stop, period)
        else:
            stop = self.x[-1]
            x = clock.ticks(stop=stop)

        return self(x)
        #return Wave(x=x,y=y, name=self.name + "(Sampled at {}".format(period))

    def shift(self, value, mode="full"):
        """ Delays the waveform by the specified value.
        """
        self.x = self.x + value
        return self

    def transpose(self):
        """ Swaps X and Y arrays.
        :return:
        """
        self.x, self.y = self.y, self.x

    def trim(self, start=None, end=None):
        """Trims a waveform's X axis to the desired start and end points"""
        if start is None:
            start = self.x[0]
        if end is None:
            end = self.x[-1]

        points = self.x[self.x >= start and self.x <= end]
        return self(points)

    def xmax(self):
        ymax = self.y.argmax()
        return self.x[ymax]

    def xmin(self):
        ymin = self.y.argmin()
        return self.x[ymin]

    def pdf(self):
        pass

    def cdf(self):
        pass

    def histogram(self):
        pass

    def rms(self):
        pass

    def slice(self, levels=None, values=[0,1]):
        """ Slices the waveform into discrete Binary values using the provided **levels** and **values**.

        :param thresholds: Y levels at which to slice.  If **None**, will use the waveform's threshold attribute.
        This can be a single item for PAM-2 coded data or a list of size log(N) for PAM-N data.

        Items in the list can be numerical values or a waveform.

        :param levels: A list of integer values that are sliced by the thresholds. Must be greater than the number
        of thresholds by 1.

        return: Returns a Binary version of the waveform, by slicing at the given thresholds and mapping the
        output to the given

        For example to slice a differential NRZ value, levels would be [0], and values would be [-1,1].   To slice
        CMOS logic waveforms, supply VDD/2 for the levels argument, and [0,1] for its values.
        """

        # If levels

        if levels is None:
            if self.threshold is not None:
                levels = (self.threshold,)
            else:
                raise ValueError("Need to provide slicing threshold.")

        # Handle the PAM-2 case since it is much easier to handle and will be the most common form.
        if len(levels) == 1:

            x0 = self.x[0]
            y0 = values[0] if self.y[0] <= levels[0] else values[1]

            x_rising = self.cross(levels[0], edge="rising")
            x_falling = self.cross(levels[0], edge="falling")

            y_rising  = np.array(int(values[1])).repeat(len(x_rising))
            y_falling = np.array(int(values[0])).repeat(len(x_falling))

            x = np.concatenate([[x0], x_rising, x_falling])
            y = np.concatenate([[y0], y_rising, y_falling])

            indices = x.argsort()
            x = x[indices]
            y = y[indices]

        else:
            raise NotImplementedError
            rising = [ self.cross(level, edge="rising") for level in levels]
            falling = [ self.cross(level, edge="falling") for level in levels]
        from .logic import Logic

        return Logic(x=x, y=y)


if __name__ == "__main__":

    import pdb
    import matplotlib.pyplot as plt
    PLOT = False

    y = np.zeros(10)
    y[4:7] = 1.0
    x=np.arange(0, 9, .01)
    a = Wave(y,interp='step')
    b = Wave(y, interp='step')

    a = a(x)
    pdb.set_trace()
    b = b(x).shift(-0.5)

    if True:
        plt.subplot(3,1,1)
        plt.plot(a.x, a.y)
        plt.subplot(3,1,2)
        plt.plot(b.x, b.y)

        plt.subplot(3,1,3)
        c = a.convolve(b)
        plt.plot(c.x, c.y)

    plt.show()

