from ...design import connections
from .save import I as save_I

class Pin(connections.Pin):
    pass

    @property
    def I(self):
        return save_I(self)



class Net(connections.Net):
    pass

class Input(connections.Input):
    pass

class Output(connections.Output):
    pass

class Global(Net):
    '''A global signal is a net that is available at all levels of hierarchy w/o
        being brought in through an explicit pin'''
    pass

GND = Global(name=0)
