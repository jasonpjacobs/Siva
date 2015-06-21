import numpy as np

from .wave import Wave

class Logic(Wave):
    def __init__(self, data=None, x=None, y=None, name=None, desc=None, width=None):

        assert len(x) == len(y)

        super().__init__(data=data, x=x, y=y, name=name, desc=desc)
        if y is not None:
            y = np.array(y).astype(int)

        self.width = width

    @property
    def interp(self):
        """Logic values should do step interpolation
        """
        return "step"

    @interp.setter
    def interp(self, value):
        assert( value in ('linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'step'))
        self._interp = value

    def to_wave(self, rise=None, fall=None, scale=1.0):
        """ Create a piecewise linear waveform based on the logic data.


        """
        if rise is not None and fall is None:
            fall = rise

        x = self.x
        y = self.y*scale

        x0 = np.array(self.x[0])
        y0 = np.array(self.y[0])

        if rise is None and fall is None:
            rise=0
            fall=0

        if rise == fall:
            # Create the data
            start_x = x[1:] - rise/2
            end_x = x[1:] + rise/2
            start_y = y[0:-1]
            end_y = y[1:]

            # Zip the points together
            mid_x = np.empty(len(start_x) + len(end_x), dtype=self.x.dtype)
            mid_y = np.empty(len(start_y) + len(end_y), dtype=self.y.dtype)
            mid_x[0::2] = start_x
            mid_x[1::2] = end_x
            mid_y[0::2] = start_y
            mid_y[1::2] = end_y

            # Append to the first point
            x = np.append(x0, mid_x)
            y = np.append(y0, mid_y)
        else:
            raise NotImplementedError

        return Wave(x=x, y=y)

    def reduce(self):
        """ Removes consecutive identical digits from the waveform.
        """

        indices = np.array([0])

        # Find the indices where transitions occur
        transitions = self.y[0:-1] != self.y[1:]
        indices = np.append(indices, transitions.nonzero()[0] + 1)

        # And return a waveform with just those indices
        return self[indices]






