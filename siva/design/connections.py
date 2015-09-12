import copy

from ..components import Registered


def convert_slice(slice_, min=None, max=None):
    """Converts Python slice objects that are written assuming Verilog conventions for bit selects

    Verilog     Meaning         Slice                   Result
    [3:0]       3 down to 0     slice(msb, lsb, -1)     [3,2,1,0]
    [0:3]       0 up to 3       slice(0, 3 + 1, 1)      [0,1,2,3]

    """
    step = slice_.step
    if slice_.step is None:
        step = 1

    sign = -1 if slice_.start > slice_.stop else 1
    start = slice_.start
    step = sign*abs(step)
    stop = slice_.stop + sign

    # Limit to min/max
    minf = __builtins__['min']
    maxf = __builtins__['max']

    if sign == 1:
        if min is not None:
            start = maxf(min, start)
        if max is not None:
            stop = minf(max + step, stop)
    else:
        if min is not None:
            stop = maxf(min + step, stop)
        if max is not None:
            start = minf(max, start)

    return slice(start, stop, step)

class Net(Registered):
    registry_name = "nets"

    bus_format = ('[', ']')

    def __init__(self, *args, name=None, parent=None, width=1, msb=None, lsb=None, index=None):
        self.name = name
        self.ports = []
        self.parent = parent
        self.width = width
        self.index = index

        self._slices = None

        # If *args* is provided, this Net is acting as a view into an existing bus
        if len(args) > 0:
            nets = args
            if not hasattr(nets, '__getitem__'):
                raise ValueError("The argument for the {} class must be a sequence".format(self.__class__.__name__))
            self._slices = [n for n in nets]  # Shallow list copy
            self.width = len(nets)
        # If width is provided, this is a new bus
        elif width > 1:
            self._slices = []
            for i in range(width):
                self._slices.append(Net(name=name, index=i))
        # If index is provided, this is a slice into an existing bus
        elif index is not None:
            pass

        if self.width > 1:
            assert index is None
            if msb is None and lsb is None:
                msb = width - 1
                lsb = 0
            self.msb = msb
            self.lsb = lsb
        else:
            self.index = index
            self.msb = 0
            self.lsb = 0

    def add_port(self, port):
        self.ports.append(port)

    @property
    def net(self):
        return self

    @property
    def path(self):
        from ..design.design import Design
        if self.parent is not None and isinstance(self.parent, Design):
            return self.parent.path + ':' + str(self)
        else:
            return str(self)

    @property
    def is_bus(self):
        return self.width > 1

    def __str__(self):
        if not self.is_bus:
            if self.index is not None:
                return self.name + self.bus_format[0] + str(self.index) + self.bus_format[1]
            return self.name
        else:
            return "{}{}{}:{}{}".format(self.name, self.bus_format[0], self.msb, self.lsb,self.bus_format[1])

    # ------------------------------------------------
    #       Bus Attributes
    # ------------------------------------------------
    def __getitem__(self, item):
        if self._slices is None:
            raise KeyError("{} is not a bus.".format(self.__class__.__name__))

        if isinstance(item, int):
            return self._slices.__getitem__(item)
        elif isinstance(item, slice):
            start = item.start if item.start is not None else self.lsb
            stop  = item.stop if item.stop is not None else self.msb
            step = abs(item.step) if item.step else 1
            indices = list(range(self.width).__getitem__(slice(min(start,stop), max(start,stop) + 1, step)))
            sign = -1 if item.start > item.stop else 1

            if sign == 1:
                indices = indices[::-1]

            msb = max(start, stop)
            lsb = min(start, stop)
            nets = [self._slices.__getitem__(i) for i in indices]

            if abs(step) == 1:
                return Net(*nets, name=self.name, msb=msb, lsb=lsb)
            else:
                return Bundle(nets, name=self.name)


class Bundle(Net):
    def __init__(self, *args, name=None):
        self._slices = args
        self.name = name
        self.width = len(args)
        self.index = None

        self.msb = len(self._slices) - 1
        self.lsb = 0

    def __str__(self):
        if not self.is_bus:
            if self.index is not None:
                return self.name + self.bus_format[0] + str(self.index) + self.bus_format[1]
            return self.name
        else:
            return "{}{}{}:{}{}".format(self.name, self.bus_format[0], self.msb, self.lsb,self.bus_format[1])

class Pin(Registered):
    registry_name = "ports"

    def __init__(self, name=None, direction=None, parent=None):

        self._net = None
        self._parent = parent
        self._name = name

        self.direction = None
        self.conn = None

    @property
    def net(self):
        """Get the Net object associated with this Pin.

        This is implemented as a property so subclasses can return
        their own flavor of Net subclass.
        """
        if self._net is None:
            self._net = Net(name=self.name)
        return self._net

    def connect(self, net):
        """Connect this port to a net
        """
        if net is None:
            raise ValueError("Error in instance port connection.  Net is 'None'. ({}:{})".format(self.parent, self.name))
        self.conn = net
        net.add_port(self)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.net.name = name

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
        if self.net is not None:
            self.net.parent = value

    @property
    def path(self):
        from ..design.design import Design
        if self.parent is not None and isinstance(self.parent, Design):
            return self.parent.path + ':' + self.name
        else:
            return self.name


    # ------------------------------------------------
    #       Bus Attributes
    # ------------------------------------------------
    def __getitem__(self, item):
        return None




class Input(Pin):
    pass

class Output(Pin):
    pass

class Global(Net):
    '''A global signal is a net that is available at all levels of hierarchy w/o
        being brought in through an explicit pin'''
    pass

GND = Global(name=0)