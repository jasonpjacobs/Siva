

from siva.old_spice.command import Command
from siva.old_spice.descriptors import Variable, FloatType, Int, EnumType, BoolType

class Analysis(Command):

    _saves = []

    def save(self, *deviceOrNodes):
        self._saves.extend(deviceOrNodes)

    @property
    def outputs(self):
        return [s.output() for s in self._saves]

class DC(Analysis):
    _props = ['lin', 'start', 'stop', 'step']

    name = "DC"
    var = Variable()
    start = FloatType()
    stop = FloatType()
    step = FloatType()

    def __init__(self, var=None, start=None, stop=None, step=None):
        self.var = var
        self.start = start
        self.stop = stop
        self.step = step
        Command.register_keyword(self, store_as="list", keyword="analyses")

    def card(self):
        txt = ".DC {} {} {} {}".format(self.var, self.start, self.stop, self.step)
        return txt

class AC(Analysis):
    """
    Type:  'LIN', 'OCT', 'DEC'
    """
    name = "AC"
    start = FloatType()
    stop = FloatType()
    points = Int()
    sweep = EnumType("lin", "oct", "dec")

    def __init__(self, start=None, stop=None, points=20, sweep="dec"):
        self.start = start
        self.stop = stop
        self.points = points
        self.sweep = sweep
        Command.register_keyword(self, store_as="list", keyword="analyses")

    def card(self):
        txt = ".AC {} {} {} {}".format(self.sweep, self.points, self.start, self.stop )
        return txt


class Tran(Analysis):
    name = "TRAN"
    start = FloatType(0)
    stop = FloatType()
    step = FloatType()
    uic = BoolType(False)

    def __init__(self, start=0, stop=None, step=None, uic=False):
        self.start = start
        self.stop = stop
        self.step = step
        self.uic = uic

        Command.register_keyword(self, store_as="list", keyword="analyses")

    def card(self):
        uic = "UIC" if self.uic else ""
        start = self.start if self.start > 0 else ""
        txt = ".TRAN {step} {stop} {start} {uic}".format(step=self.step, stop=self.stop,
                                                         start=start, uic=uic)
        return txt


