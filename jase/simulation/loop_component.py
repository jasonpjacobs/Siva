
import numpy as np

from .component import AnalysisComponent

class LoopVariable:
    def __init__(self, name, target, start, stop, step=None, n=None, endpoint=True, space="linear"):

        if n is None and step is None:
            raise ValueError("Either 'step' or 'N' must be provided")

        #Calculate n, so we can use lin/logspace functions
        if step is not None and n is None:
            n = int((stop - start)/step)
            if endpoint:
                n += 1


        if space == "linear":
            values = np.linspace(start, stop, n, endpoint)
        elif space == "log":
            values = np.logpace(start, stop, n, endpoint)

        self.name = name
        self.target = target
        self.start = start
        self.stop = stop
        self.n = n
        self.values = values
        self.reset()

    def __iter__(self):
        self.reset()
        return self

    def __next__(self):
        if self.i == self.n:
            raise StopIteration

        self.i += 1
        return self.values[self.i]

    def __len__(self):
        return self.n

    def __getitem__(self, item):
        return self.values[self.i]

    def reset(self):
        self.i = -1


class LoopComponent(AnalysisComponent):
    def __init__(self, parent=None, vars=None):
        if isinstance(vars, LoopVariable):
            vars = (vars,)
        super().__init__(parent, children={(v.name,v ) for v in vars})

    def __len__(self):
        return np.sum([len(var) for var in self.vars.values()])

    @property
    def vars(self):
        return self._children
