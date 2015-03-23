from ...design import Design

class Circuit(Design):

    def card(self):
        txt = []

        # Inst name
        txt.append("X_{name}".format(name=self.name))

        # Pin ocnnection
        for pin in self.ports.values():
            txt.append(pin.conn.name)

        # Design name
        txt.append(self.cell_name)

        # Parameters
        if self.params:
            # TODO: Implement spice level params
            pass

        return [" ".join(txt)]


    def subckt_card(self):
        txt = []
        pin_txt = " ".join(self.ports)
        txt.append(".SUBCKT {} {}".format(self.cell_name, pin_txt))
        for inst in self.instances.values():
            txt.append("  " + inst.card())
        txt.append(".ENDS")
        return txt


