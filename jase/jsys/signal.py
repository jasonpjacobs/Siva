from weakref import WeakKeyDictionary
from .simulation import Sim
from jwave.wave import Wave
from .event import SignalValueChangeEvent, DelayEvent
import pdb

class Signal(Wave):

    def __init__(self, default=None, name=None):
        super().__init__(name=name)
        self.default = default

        self._callbacks = []

    def __copy__(self):
        copy = self.__class__(name=self.name, default=self.default)
        copy._callbacks = self._callbacks
        return copy

    def after(self, time):
        event = DelayEvent()


class Logic(Signal):
    pass
