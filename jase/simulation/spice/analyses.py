from ..variable import Float, Bool
from ...components.directive import Directive

class Analysis(Directive):
    registry_name = "analyses"

    #def _store(self,  class_dct, registry_name):
    #    self._store_as_key_value_pair( class_dct=class_dct, registry_name=registry_name)


class Tran(Analysis):
    analysis_name = "tran"
    start = Float()
    step = Float()
    stop = Float()
    uic = Bool()

    def __init__(self, start=0, stop=None, step=None, uic=False):
        super().__init__()

        self.start = start
        self.stop = stop
        self.step = step
        self.uic = uic
        self.name = 'tran'

    def card(self):
        txt = ".TRAN {step} {stop} {start} {uic}".format(**self._param_dict)
        return [txt]

    @property
    def _param_dict(self):
        dct = super()._param_dict

        if self.uic is not True:
            dct['uic'] = ""

        if self.start == 0:
            dct['start'] = ''

        return dct
