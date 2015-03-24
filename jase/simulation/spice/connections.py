from ...design import connections
from .save import I as save_I
from .save import V as save_V

class Pin(connections.Pin):

    @property
    def I(self):
        return save_I(self)

    @property
    def V(self):
        return self.net.V

    @property
    def net(self):
        """Get the Net object associated with this Pin.

        This is implemented as a property so subclasses can return
        their own flavor of Net subclass.
        """
        if self._net is None:
            self._net = Net(name=self.name)
        return self._net

class Net(connections.Net):

    @property
    def V(self):
        return save_V(self)

class Input(connections.Input):
    @property
    def I(self):
        return save_I(self)

    @property
    def V(self):
        return self.net.V

    @property
    def net(self):
        """Get the Net object associated with this Pin.

        This is implemented as a property so subclasses can return
        their own flavor of Net subclass.
        """
        if self._net is None:
            self._net = Net(name=self.name)
        return self._net

class Output(connections.Output):
    @property
    def I(self):
        return save_I(self)

    @property
    def V(self):
        return self.net.V

    @property
    def net(self):
        """Get the Net object associated with this Pin.

        This is implemented as a property so subclasses can return
        their own flavor of Net subclass.
        """
        if self._net is None:
            self._net = Net(name=self.name)
        return self._net

class Global(Net):
    '''A global signal is a net that is available at all levels of hierarchy w/o
        being brought in through an explicit pin'''

    @property
    def V(self):
        return save_V(self)

GND = Global(name=0)
