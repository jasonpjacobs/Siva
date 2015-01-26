
import numpy as np
import itertools

from .component import Component

class LoopVariable:
    def __init__(self, name, target, start, stop, step=None, n=None, endpoint=True, space="linear"):

        if n is None and step is None:
            raise ValueError("Either 'step' or 'N' must be provided")

        if step is not None and n is None:
            if endpoint:
                # arange normally excludes the endpoint.  In order to capture
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
        if self.i == self.n:
            raise StopIteration

        self.current = self.values[self.i]

        if callable(self.target):
            pass
        else:
            #print("{}: Setting target {} to {}".format(self.i, self.target, self.values[self.i]))
            #self.target = self.values[self.i]
            pass



        return self.values[self.i]

    def __len__(self):
        return self.n

    def __getitem__(self, item):
        return self.values[self.i]

    def reset(self):
        self.i = -1

class LoopComponent(Component):
    def __init__(self, parent=None, vars=None):
        if isinstance(vars, LoopVariable):
            vars = (vars,)
        super().__init__(parent, children={(v.name,v ) for v in vars})

    def __len__(self):
        return np.sum([len(var) for var in self.vars.values()])

    def __iter__(self):
        self._iterators = [var.__iter__() for var in self.vars]
        return self

    def __next__(self, i=0):
        pass

    def __iter_next__(self, i):
        iterator = self.vars[i]
        for value in iterator:
            print("{} Iterator {} is {}".format("  "*i, iterator.name, iterator.current))
            if i < len(vars) - 1:
                yield iter_all(i+1)
            yield

    @property
    def vars(self):
        return self.children




