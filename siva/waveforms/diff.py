from .wave import Wave
import numpy as np
import numbers

class Diff(Wave):
    """A differential waveform, described in terms of positive/negative or differential/common mode components.
    """
    def __init__(self, x=None, pos=None, neg=None, diff=None, cm=None,
                 name=None, desc=None, interp='linear', default=None):
        self.name = name
        self.desc = desc
        self.interp = interp
        self.default = default

        self._x = []
        self._y = []
        self._diff = None
        self._cm = None
        self._pos = None
        self._neg = None
        self._build_mode = False

        if (x, pos, neg, diff, cm) == (None, None, None, None, None):
            # Create an empty Wave that can be built incrementally
            # (via simulation, for example)
            self._build_mode = True
        else:
            self._parse_inputs(x, pos, neg, diff, cm)

    def _parse_inputs(self, x, pos, neg, diff, cm):

        # Check to see if pure numbers were given
        # for any of the components.  If so, duplicate them for each
        # value

        if pos is not None or neg is not None:
            if (diff is not None) or (cm is not None):
                raise ValueError("Differntial signals must be specified with pos/neg or diff/cm components")

            if not isinstance(pos, np.ndarray):
                if isinstance(pos, numbers.Number):
                    pos = np.ones(len(neg))*pos
                else:
                    pos = np.array(pos)

            if not isinstance(neg, np.ndarray):
                if isinstance(neg, numbers.Number):
                    neg = np.ones(len(pos))*neg
                else:
                    neg = np.array(neg)

            self._pos = pos
            self._neg = neg

        if diff is not None or cm is not None:
            if (pos is not None) or (neg is not None):
                raise ValueError("Differential signals must be specified with pos/neg or diff/cm components")

            if not isinstance(diff, np.ndarray):
                if isinstance(pos, numbers.Number):
                    diff = np.ones(len(cm))*diff
                else:
                    diff = np.array(diff)

            if not isinstance(cm, np.ndarray):
                if isinstance(cm, numbers.Number):
                    cm = np.ones(len(diff))*cm
                else:
                    cm = np.array(cm)

            self._diff = diff
            self._cm = cm

        if not isinstance(x, np.ndarray):
            x = np.array(x)
        self.x = x

    @property
    def y(self):
        if isinstance(self.diff[0], complex):
            return abs(self.diff)
        return self.diff

    @y.setter
    def y(self, value):
        self.diff = value

    @property
    def diff(self):
        if self._diff is None:
            self._diff = self._pos - self._neg
        return self._diff

    @diff.setter
    def diff(self, value):
        self._diff = value

        # Reset the pos/neg components
        self._pos = None
        self._neg = None

    @property
    def cm(self):
        if self._cm is None:
            self._cm = (self.p + self.n)/2
        return self._cm

    @cm.setter
    def cm(self, value):
        self._cm = value

        # Reset the pos/neg components
        self._pos = None
        self._neg = None

    @property
    def pos(self):
        if self._pos is None:
            self._pos = self._diff/2 + self._cm
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value

        # Reset diff/cm components
        self._cm = None
        self._diff = None

    @property
    def neg(self):
        if self._neg is None:
            self._neg = -1*(self._diff)/2 + self._cm

        # Reset diff/cm components
        self._cm = None
        self._diff = None

