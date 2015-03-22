from ..variable import Variable, Float, Bool
from ...components.directive import Directive

class Analysis(Directive):
    registry_name = "analyses"

    #def _store(self,  class_dct, registry_name):
    #    self._store_as_key_value_pair( class_dct=class_dct, registry_name=registry_name)


class Tran(Analysis):
    analysis_name = "tran"
    step = Float()
    stop = Float()
    uic = Bool()

    def __init__(self, start=0, stop=None, step=None, uic=False):
        super().__init__()

        self.start = start
        self.stop = stop
        self.step = step
        self.uic = uic

    def card(self):
        uic = "UIC" if self.uic else ""
        start = self.start if self.start > 0 else ""
        txt = ".TRAN {step} {stop} {start} {uic}".format(step=self.step, stop=self.stop,
                                                         start=start, uic=uic)
        return [txt]

