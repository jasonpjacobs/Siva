
import numpy as np
import itertools

from .component import AnalysisComponent

class LoopVariable:
    def __init__(self, name, target, start, stop, step=None, n=None, endpoint=True, space="linear"):

        if n is None and step is None:
            raise ValueError("Either 'step' or 'N' must be provided")

        #Calculate n, so we can use lin/logspace functions
        if step is not None and n is None:
            if endpoint:
                # Arange normally exludes the endpoint.  In order to capture
                # it, we'll extend it by an amount smaller than the step size
                stop = stop + step/2
            if space == "linear":
                values = np.arange(start=start, stop=stop, step=step)
                n = len(values)
            if space == "log":
                raise NotImplementedError
        else:
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
        self.i += 1
        if callable(self.target):
            pass
        else:
            print("{}: Setting target {} to {}".format(self.i, self.target, self.values[self.i]))
            self.target = self.values[self.i]

        if self.i == self.n:
            raise StopIteration


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

    def __iter__(self):
        self.values = itertools.product(self.vars.values())
        return self

    def __next__(self):
        return self.values.__next__()

