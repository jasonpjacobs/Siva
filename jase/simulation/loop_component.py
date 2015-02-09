
import numpy as np
import itertools

from .base_component import BaseComponent

class LoopVariable:
    def __init__(self, name, target, start=None, stop=None, step=None, n=None, values=None, endpoint=True, space="linear"):

        if values is not None:
            self.values = values
            n = len(values)
        elif start is not None and stop is not None:

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
        self.current = self.values[0]
        return self

    def __next__(self):
        self.i += 1
        if self.i == self.n:
            raise StopIteration

        self.current = self.values[self.i]

        return self.values[self.i]

    def __len__(self):
        return self.n

    def reset(self):
        self.i = -1

    def eval(self, globals, locals):
        target = eval(self.target, globals, locals)
        if callable(target):
            exec("{}({})".format(self.target, self.current), globals, locals)
        else:
             exec("{}={}".format(self.target, self.current), globals, locals)

    def set(self, value):
        self.current = value

class LoopComponent(BaseComponent):
    def __init__(self, parent=None, vars=None, children=None, namespace=None, name=None, measurements=None, **kwargs):
        if isinstance(vars, LoopVariable):
            vars = (vars,)
        self.loop_vars = vars
        super().__init__(parent=parent, children=children, name=name, vars=None, measurements=measurements, **kwargs)

        if namespace is not None:
            self._namespace = namespace
        else:
            self._namespace = {}

    def __len__(self):
        return np.product([len(var) for var in self.loop_vars])

    def __iter__(self):
        self._iterators = itertools.product(*self.loop_vars)
        return self

    def __next__(self):
        values = self._iterators.__next__()
        for var, val in zip(self.loop_vars, values):
            var.set(val)
            var.eval(globals(), self._namespace)
        return values

    # BaseComponent interface
    def init(self):
        """
        """
        self.__iter__()

    def reset(self):
        """
        Used to reset the component to the initial state after having been run.
        """
        self.__iter__()

    def execute(self):
        self.__next__()


