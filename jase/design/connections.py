
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

class Pin(Registered):
    registry_name = "ports"
    def __init__(self, name=None, direction=None):
        self.name = name
        self.direction = None
        self.net = None

    def connect(self, net):
        self.net = net
        net.add_port(self)


class Input(Pin):
    pass

class Output(Pin):
    pass