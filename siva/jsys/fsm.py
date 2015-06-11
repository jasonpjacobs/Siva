from jsys import Input, Output, Signal

class FSM(jsys.module.Module):
    clk = Input()


    @posedge(clk)
    def next_state(self):
