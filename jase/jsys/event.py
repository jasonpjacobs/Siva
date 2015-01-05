from itertools import count

from .simulation import Sim
import weakref

class Cached(type):
    """ Modified from Python Cookbook, 3rd edition.recipe 9.13
    """
    @classmethod
    def __prepare__(cls, name, bases, *, keys=None):
        return super().__prepare__(name, bases)

    def __new__(cls, name, bases, dct, *, keys=None):
        return super().__new__(cls, name, bases, dct)

    def __init__(self, name, bases, dct, *, keys=None):
        super().__init__(name, bases, dct)
        self.keys = keys
        if keys is not None:
            print("Implementing instance caching for", name, keys)
        self.__cache = weakref.WeakValueDictionary()

    def __call__(self, *args, **kwargs):
        if self.keys:
            key = tuple([arg for arg in args if arg in self.keys])
            key = args
            print("  --> key ", key)
            import pdb
            #pdb.set_trace()
            if key in self.__cache:
                print("cache hit!")
                obj = self.__cache[key]
                print("Cachec obj", id(obj))
                return obj
        obj = super().__call__(*args)
        self.__cache[args] = obj
        print("New obj", id(obj))
        return obj





class Event(metaclass=Cached):
    # To allow different classes of events to be ranked within a time slot
    order = 0

    _event_types = ["SignalValueUpdate", "CallbackEvent"]
    _event_priority = {v: k for k, v in enumerate(_event_types)}

    def __init__(self, time=None, n=None, order=None, tags=None):
        # If time is None, then get the current time
        if time is None:
            time = Sim().now()
        else:
            self.time = Sim().round(time)

        self.n = n

        if order is not None:
            self.order = order

        self.tags = tags

        self.executed = False

    def __call__(self):
        raise NotImplementedError

    def __lt__(self, other):
        if  self.time != other.time:
            return self.time < other.time
        elif self.order != other.order:
            return self.order < other.order
        else:
            return self.n < other.n

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.time)



class SignalValueChangeEvent(Event):
    order = 1

    def exec_(self):
        pass

class CallbackEvent(Event, keys=('func', 'inst', 'time')):
    def __init__(self, func, inst, time=None, n=None, order=None, tags=None):
        self.inst = inst
        self.func = func

        super().__init__(time, n, order, tags)

    def __repr__(self):
        return "{}({}@{})".format(self.__class__.__name__, self.func.__name__, self.time)

    def __call__(self):
        self.func(self.inst)


class DelayEvent(Event):
    def __init__(self, time ):
        pass

