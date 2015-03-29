
from ..components import Registered

class Net(Registered):
    registry_name = "nets"
    def __init__(self, name, parent=None):
        self.name = name
        self.ports = []
        self.parent = parent

    def add_port(self, port):
        self.ports.append(port)

    @property
    def net(self):
        return self

    @property
    def path(self):
        from ..design.design import Design
        if self.parent is not None and isinstance(self.parent, Design):
            return self.parent.path + ':' + self.name
        else:
            return self.name

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

class Input(Pin):
    pass

class Output(Pin):
    pass

class Global(Net):
    '''A global signal is a net that is available at all levels of hierarchy w/o
        being brought in through an explicit pin'''
    pass

GND = Global(name=0)