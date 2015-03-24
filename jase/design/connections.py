
from ..components import Registered

class Net(Registered):
    registry_name = "nets"
    def __init__(self, name, *args):
        self.name = name
        self.ports = []

    def add_port(self, port):
        self.ports.append(port)

    @property
    def net(self):
        return self

    @property
    def path(self):
        return self.parent.path + '.' + self.name

class Pin(Registered):
    registry_name = "ports"
    def __init__(self, name=None, direction=None):
        self.net = Net(name=name)
        self.name = name
        self.direction = None
        self.conn = None


    def connect(self, net):
        """Connect this port to a net
        """
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
    def path(self):
        return self.parent.path + ':' + self.name

class Input(Pin):
    pass

class Output(Pin):
    pass

class Global(Net):
    '''A global signal is a net that is available at all levels of hierarchy w/o
        being brought in through an explicit pin'''
    pass

GND = Global(name=0)