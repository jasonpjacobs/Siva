from ...design import Design

class Circuit(Design):

    def card(self):
        txt = []
        pin_txt = " ".join(self.ports)
        txt.append(".SUBCKT {} {}".format(self.name, pin_txt))
        for inst in self.instances.values():
            txt.append("  " + inst.card())
        txt.append(".ENDS")
        return txt


