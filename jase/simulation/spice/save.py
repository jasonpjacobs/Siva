from ...components.directive import Directive

class Save(Directive):
    registry_name = "saves"
    token = ""


    def __init__(self, *args, analysis=None, format='raw'):
        from .connections import Net, Pin, GND

        super().__init__()

        self.analysis = analysis

        requests = []
        for arg in args:
            # TODO:  Check if net, pins are voltage or current domain to determine the correct save type
            if isinstance(arg, Net):
                requests.append(arg.V)
            elif isinstance(arg, Pin):
                requests.append(arg.pin.net.V)
            elif isinstance(arg, Output):
                requests.append(arg)
            else:
                raise TypeError("Argument to Save must be a net, pin, or output request.")

        self.requests = requests
        self.format = format
        self.name = 'save'

    @staticmethod
    def card(outputs, format='raw', analysis='tran'):
        cards = []
        cards.append(".PRINT {analysis} format={format} {outputs}".format(analysis=analysis,
                format=format, outputs=" ".join(outputs)))

        return cards

    def outputs(self):
        # [item for sublist in l for item in sublist]
        outputs = []
        for request in self.requests:
            outputs.extend(request.outputs())
        return outputs


class Output:
    """ An output (waveform) save request)
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


    def __init__(self, p, n=None):


        from .connections import GND
        if n is None:
            n = GND
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
        # Xyce format:
        # return ["{}{}({})".format(self.token, str(self.pin.name), txt)]

        # Spice/NGspice format:
        return ["{}({})".format(self.token, txt)]

class I_src(Output):
    """Probe request for a the current of a voltage source"""

    token = "I"
    def __init__(self, src):
        self.src = src

    def outputs(self):
        txt = str(self.src.path)
        # Spice/NGspice format:
        return ["{}({})".format(self.token, txt)]