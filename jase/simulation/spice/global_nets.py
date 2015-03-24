from ...design import Pin, Net

class Global(Net):
    '''A global signal is a net that is available at all levels of hierarchy w/o
        being brought in through an explicit pin'''
    pass

GND = Global(name=0)

# class GND(Global):
#     '''A global ground net.  Node '0' is Spice simulators.
#     '''
#
#     __shared_state = {}  # Borg pattern
#     def __init__(self):
#         self.__dict__ = self.__shared_state
#         super().__init__(name='0')