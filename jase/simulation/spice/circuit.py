from ...design.design import Design, DesignMeta
from ...components.component import ComponentNamespace
from .connections import Net

class CircuitMeta(DesignMeta):
    @classmethod
    def __prepare__(metacls, name, bases):
        return ComponentNamespace(default=Net)

class Circuit(Design, metaclass=CircuitMeta):

    def card(self):
        txt = []

        # Inst name
        txt.append("{name}".format(name=self.inst_name))

        # Pin connections
        # Pin connections
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
            txt.extend(inst.card())
        txt.append(".ENDS")
        return txt

    @property
    def inst_name(self):
        """Called during netlisting to convert our internal name to one
        compatible with a target design language
        """
        return "X_" + str(self.name)


