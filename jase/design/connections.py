
from ..components import Registered

class Net(Registered):
    registry_name = "nets"
    def __init__(self, name, *args):
        self.name = name
        self.ports = []

    def add_port(self, port):
        self.ports.append(port)

class Pin(Registered):
    registry_name = "ports"
    def __init__(self, name=None, direction=None):
        self.name = name
        self.direction = None

    def connect(self, conn):
        self.conns = conn
        conn.add_port(self)

class Input(Pin):
    pass

class Output(Pin):
    pass