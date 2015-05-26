import pdb
from .signal import Signal
from .simulation import Sim
from .event import CallbackEvent, DelayEvent, SignalValueChangeEvent

class ModuleMeta(type):
    """
    Metaclass that examines the Signals, Pins, and Parameters of a
    module definition and stores them in unique dictionaries
    """
    def a(metacls, name, bases, dct):
        instance = super().__new__(metacls, name, bases, dct)
        return instance

    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)

        cls.__signals__ = {}

        for k,v in cls.__dict__.items():
            if isinstance(v, Signal):
                cls.__signals__[k] = v
                v.name = k

class Module(metaclass=ModuleMeta):
    def __init__(self, name):
        self.name = name

        # Create instances of the signals in the class dictionary
        # and populate the instance namespace
        self.__signals__ = {}
        for name, signal in self.__class__.__signals__.items():
            self.__dict__[name] = self.__signals__[name] = signal.__copy__()

    def __getattr__(self, item):
        if item in self.__signals__:
            return self.__signals__[item]._y[-1]

    def __setattr__(self, name, value):
        # Special signal attribute handling
        if name in self.__signals__:
            signal = self.__signals__[name]
            signal.append(Sim.time, value)
            if isinstance(value, SignalValueChangeEvent):
                # Schedule this event
                print("Scheduling signal value change for", value.time)
                Sim().add_event(value)

            # See if the signal wants a callback scheduled
            if len(signal._callbacks) > 0:
                for cb in signal._callbacks:
                    event = CallbackEvent(cb, self, Sim().now())
                    Sim().add_event(event)

        else:
            object.__setattr__(self, name, value)

    def _finalize(self):
        for signal in self.__signals__.values():
            signal._build_mode = False

