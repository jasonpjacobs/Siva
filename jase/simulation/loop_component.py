
import numpy as np
import itertools
import collections

from .base_component import BaseComponent
from .variable import Variable
from ..components.parameter import Parameter
class LoopVariable(Variable):
    def __init__(self, name, target, start=None, stop=None, step=None, n=None,
                 values=None, endpoint=True, space="linear", desc=None):

        super().__init__(name, target, desc)

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
        self.value = self.values[0]
        return self

    def __next__(self):
        self.i += 1
        if self.i == self.n:
            raise StopIteration

        self.value = self.values[self.i]

        return self.values[self.i]

    def __len__(self):
        return self.n

    def reset(self):
        self.i = -1

    def set(self, value):
        self._value = value

class LoopComponent(BaseComponent):
    def __init__(self, parent=None, vars=None, children=None, name=None, measurements=None, **kwargs):

        if isinstance(vars, LoopVariable):
            vars = (vars,)
        self.loop_vars = vars

        # Convert the parameters from a list to a dict
        params = collections.OrderedDict()
        if vars is not None:
            for v in vars:
                params[v.name] = v
        super().__init__(parent=parent, children=children, name=name, params=params, measurements=measurements, **kwargs)

    def __len__(self):
        return np.product([len(var) for var in self.loop_vars])

    def __iter__(self):
        if self.root.log:
            self.root.log.debug("{}: Loop __iter__".format(self.inst_name))
        self._iterators = itertools.product(*self.loop_vars)
        self._i = 0
        return self

    def __next__(self):
        if self.root.log:
            self.root.log.debug("{}: Loop __next__".format(self.inst_name))
        self._i += 1
        values = self._iterators.__next__()

        """
        for var, val in zip(self.loop_vars, values):
            var.set(val)
            var.eval(globals(), self.root.namespace)
            if self.root.log:
                self.root.log.debug("{}: Set '{}' to {}".format(self.inst_name, var.target, val))
        return values
        """
        var_vals = zip([v.name for v in self.loop_vars], values)
        inst_name = self.name + "_" + str(self._i)
        loop_iteration = self.clone(inst_name=inst_name)

        # TODO:  Can we do this using descriptors?
        for var, val in var_vals:
            loop_iteration.params[var].value = val
        return loop_iteration

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
        for param in self.params.values():
            param.eval(globals(), self.namespace)

    def _measure(self):
        """Loop component implementation
        """
        if len(self.measurements) > 0:
            super()._measure()
        self.measure()



