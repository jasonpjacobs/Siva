
from ..signal import Diff, Analog, Logic, Supply, Param
from ..module import Module
from MyProject.domains import VDDCore

class VGA(Module):
    vdd         = Supply(domain=VDDCore)
    v_in        = Diff(Analog)
    v_out       = Diff(Analog)
    gain_ctl    = Logic(w=8, domain=vdd)

    gain = Analog()

    k_gain = Param(.033) # 10mV*code/V --> +/- 6.6 V/V

    @event
    def amp(self):
        self.v_out = self.v_in * self.gain

    @event(gain_ctl)
    def gain(self):
        assert self.gain_ctl in range(63)





