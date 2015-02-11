from ..components import Component
from ..resources.disk_resources import LocalDiskManager
from ..simulation.table import Table

import logging
import h5py
import os

import collections
class BaseComponent(Component):
    """ Base class for all simulation components

    This class defines how each component is executed.
    """

    def __init__(self, parent=None, children=None, name=None, vars=None, measurements=None, work_dir=".",
                 log_file = None):
        super().__init__(parent=parent, children=children, name=name)

        if vars is None:
            vars = collections.OrderedDict()

        if measurements is None:
            measurements = collections.OrderedDict()

        self._vars = vars
        self._measurements= measurements

        self.work_dir = work_dir

        self.results = Table()

        self.log_file = log_file
        self.log = None

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

        # Create a log file
        self.setup_logging()

        # Create a results table
        self.results = Table()

        self.init()
        for component in self.children.values():
            component._init()

    def setup_logging(self):
        if self.log_file is not None:
            path = os.path.join(self.work_dir, self.log_file)
            self.log = logging.getLogger(self.log_file)
            logging.basicConfig(filename=path, level=logging.DEBUG)

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)

            # add ch to logger
            self.log.addHandler(ch)

            self.log_file = path

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

        if self.root.log:
            self.root.log.debug("{} component executed".format(self.name))

        for _ in self:
            self._i += 1
            self.execute()
            for component in self.children.values():
                self._n += 1
                component._execute()
            self._measure()

    def _measure(self):
        # Evaluate all measurement statements
        if self.root.log:
            self.root.log.debug("{}: Evaluating measurements".format(self.name))

        for m in self._measurements:
            m.evaluate(self._namespace)

        # If the measure method was overridden, call it.
        self.measure()

        # Now record input variables and measurement values
        # into the results table

        record = {}
        for v in self._vars:
            record[v.name] = v.value

        # As well as the measured values
        for m in self._measurements:
            record[m.name] = m.value

        # Add it to the results table
        self.results.add_row(record)



    def _final(self):
        if self.root.log:
            self.root.log.debug("{}: Final postprocessing".format(self.name))

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


