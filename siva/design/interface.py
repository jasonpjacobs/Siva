""" Classes used to group signals into busses and interfaces.
"""
from ..components.component import Registered

class Bus(Registered):
    """ A Bus is a sequence of pins or nets all of the same type.
    """
    registry_name = "ports"
    
    def __init__(self, *sigs, **kwsigs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        pass



