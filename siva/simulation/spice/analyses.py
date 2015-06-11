from ...components.parameter import Float, Bool, Parameter, String, Integer
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

    def __init__(self, start=0, stop=None, step=None, uic=False, name='tran'):
        super().__init__()

        self.start = start
        self.stop = stop
        self.step = step
        self.uic = uic
        self.name = name

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


class DC(Analysis):
    analysis_name = "DC"
    var = Parameter()
    start = Float()
    stop = Float()
    step = Float()

    def __init__(self, var=None, start=None, stop=None, step=None, name='DC'):
        super().__init__()

        self.var = var
        self.start = start
        self.stop = stop
        self.step = step

        self.name = name

    def card(self):
        txt = ".DC {var} {start} {stop} {step}".format(**self._param_dict)
        return [txt]

class AC(Analysis):
    """
    Type:  'LIN', 'OCT', 'DEC'
    """
    analysis_name = "AC"

    start = Float()
    stop = Float()
    points = Integer()
    sweep = String()

    def __init__(self, start=None, stop=None, points=20, sweep="dec", name='AC'):
        super().__init__()

        self.start = start
        self.stop = stop
        self.points = points
        self.sweep = sweep
        self.name = name


    def card(self):
        txt = ".AC {sweep} {points} {start} {stop}".format(**self._param_dict)
        return [txt]

