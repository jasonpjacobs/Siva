from ...components.directive import Directive
from .global_nets import GND

class Save(Directive):
    registry_name = "saves"
    token = ""

    def __init__(self, *requests, analysis=None, format='raw'):
        super().__init__()
        self.analysis = analysis

        for request in requests:
            assert isinstance(request, Output)

        self.requests = requests
        self.format = format

    def card(self):
        cards = []

        if self.analysis is None:
            analysis = self.parent.analyses[0].analysis_name
        else:
            analysis = self.analysis

        for request in self.requests:
            for output in request.outputs():
                cards.append(".PRINT {analysis} format={format} {output}".format(analysis=analysis,
                    format=self.format, output=output))

        return cards

class Output:
    """ An output (waveform) request)
    """

class Power(Output):

    def __init__(self, p, n):
        self.p = p
        self.n = n

        self.saves = [V(p,n), I(p)]

    def outputs(self):
        outputs = []
        for save in self.saves:
            outputs.extend(save.outputs())

        return outputs

class V(Output):
    token = "V"
    def __init__(self, p, n=GND):
        self.p = p
        self.n = n

    def outputs(self):
        return ["{}({})".format(self.token, self.p.path, self.n.path)]


class I(Output):
    token = "I"
    def __init__(self, p):
        self.pin = p

    def outputs(self):
        txt = str(self.pin.parent.path)
        return ["{}{}({})".format(self.token, str(self.pin.name), txt)]
