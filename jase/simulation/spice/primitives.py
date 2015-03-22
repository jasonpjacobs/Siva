from ...design import Design

class Primitive(Design):

    def card(self):
        raise NotImplementedError

    def instance_designs(self, dct=None):
        """Primitives have no instances, by definition.
        """
        return dct


    def subckt_card(self):
        return None

