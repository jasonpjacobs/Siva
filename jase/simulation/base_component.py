from ..components import Component
from ..resources.disk_resources import LocalDiskManager
from ..simulation.table import Table

import h5py

import collections
class BaseComponent(Component):
    """ Base class for all simulation components

    This class defines how each component is executed.
    """

    def __init__(self, parent=None, children=None, name=None, vars=None, measurements=None, work_dir="."):
        super().__init__(parent=parent, children=children, name=name)

        if vars is None:
            vars = collections.OrderedDict()

        if measurements is None:
            measurements = collections.OrderedDict()

        self._vars = vars
        self._measurements= measurements

        self.work_dir = work_dir

        self.results = Table()

    @property
    def disk_mgr(self):
        if not hasattr(self,'_disk_mgr') or self._disk_mgr is None:
            raise AttributeError
        return self._disk_mgr

    @disk_mgr.setter
    def disk_mgr(self, value):
        self._disk_mgr = value

    def start(self):
        self._init()
        try:
            self._execute()
        except StopIteration:
            pass
        self._final()

    def _init(self):
        """ The first step in a simulation.
        * Initialize local variables.
        * Creates local directories on the work disk.
        """

        # Create work area.
        root = self.root
        disk_mgr = root.disk_mgr
        if self is self.root:
            disk_mgr.start()
        subdirs = [comp.name for comp in self.path_components]
        request = disk_mgr.request(job=self, subdirs = subdirs)
        self.work_dir = request.path

        # Create a results table
        self.results = Table()

        self.init()
        for component in self.children.values():
            component._init()

    def _reset(self):
        """
        Used to reset the component to the initial state after having been run.
        """
        self.reset()
        for component in self.children.values():
            component._reset()

    def _execute(self):
        """ Execute the component's main task.  Simulation components will run the simulation. Loop components
        will increment and set loop variables.  Search components will start a new set of trials.
        """
        self._n = 0
        self._i = 0
        for run in self:
            self._i += 1
            self.execute()
            for component in self.children.values():
                self._n += 1
                component._execute()
            self._measure()

    def _measure(self):
        # Default implementation simple evaluates the measurement statements.
        for m in self._measurements:
            m.evaluate(self._namespace)

        results = {}
        for v in self._vars:
            results[v.name] = v.value

        for m in self._measurements:
            results[m.name] = m.value

        # Add it to the results table
        self.results.add_row(results)

        self.measure()

    def _final(self):
        for component in self.children.values():
            component._final()
        self.final()

    def __iter__(self):
        return self

    def __next__(self):
        # By default, just execute once
        if self._i > 0:
            raise StopIteration

    def init(self):
        """ The first step in a simulation.
        * Initialize local variables.
        * Creates local directories on the work disk.
        """
        pass

    def reset(self):
        """
        Used to reset the component to the initial state after having been run.
        """
        pass

    def execute(self):
        pass

    def measure(self, results=None):
        pass


    def final(self):
        pass

    def init(self):
        """ The first step in a simulation.
        * Initialize local variables.
        * Creates local directories on the work disk.
        """
        pass

    @property
    def editor(self):
        pass


