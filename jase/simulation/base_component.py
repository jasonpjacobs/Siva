from ..components import Component
from ..resources.disk_resources import LocalDiskManager
from ..simulation.table import Table

import logging
import threading
import h5py
import os

import collections
class BaseComponent(Component):
    """ Base class for all simulation components

    This class defines how each component is executed.
    """

    # Instance dicts to copy when cloning
    _dicts = ['measurements']

    def __init__(self, parent=None, children=None, name=None, params=None, measurements=None, work_dir=".",
                 log_file=None, disk_mgr=None, parallel=False):
        super().__init__(parent=parent, children=children, name=name)

        if measurements is None:
            measurements = collections.OrderedDict()

        if params is not None:
            # If given a dict, convert to a list
            if hasattr(params, 'values'):
                params = params.values()
            # Then update the parameter dictionary
            for param in params:
                self.params[param.name] = param

        self.measurements = measurements

        self.work_dir = work_dir
        self.results = Table()

        self.log_file = log_file
        self.log = None

        self.disk_mgr = disk_mgr

        self.parallel = parallel

    @property
    def disk_mgr(self):
        if not hasattr(self,'_disk_mgr'):
            return LocalDiskManager(root=self.work_dir)
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
        if self is self.root and disk_mgr is not None:
            disk_mgr.start()

        for comp in self.path_components:
            if comp.name is None:
                raise ValueError("Component must have a name: {}".format(self))
        subdirs = [comp.name for comp in self.path_components]

        if disk_mgr:
            request = disk_mgr.request(job=self, subdirs=subdirs)
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
        if self.root.log:
            self.root.log.debug("{} component executed".format(self.inst_name))

        threads = []
        for iteration in self:
            iteration.execute()
            # Execute each child in its own thread
            for component in iteration.children.values():
                thread = threading.Thread(target=component._execute)
                threads.append(thread)

            if self.parallel:
                for thread in threads:
                    thread.start()
                # Wait for all to finish
                for thread in threads:
                    thread.join()
            else:
                for thread in threads:
                    thread.start()
                    thread.join()


            # Perform measurements
            iteration._measure()

    def _measure(self):
        # Evaluate all measurement statements
        if self.root.log:
            self.root.log.debug("{}: Evaluating measurements".format(self.inst_name))

        for m in self.measurements:
            m.evaluate(self.namespace)

        # If the measure method was overridden, call it.
        self.measure()

        # Now record input variables and measurement values
        # into the results table

        record = {}
        if self.namespace is None:
            pass
        record.update(self.namespace)

        # As well as the measured values
        for m in self.measurements:
            record[m.name] = m.value

        # Add it to the results table
        self.results.add_row(record)

    def _final(self):
        if self.root.log:
            self.root.log.debug("{}: Final postprocessing".format(self.inst_name))

        for component in self.children.values():
            component._final()
        self.final()

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        # By default, just execute once
        if self._i > 0:
            raise StopIteration
        self._i += 1
        return self

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

    @property
    def editor(self):
        pass

    @property
    def inst_name(self):
        if self._inst_name is not None:
            return self._inst_name
        else:
            return self.name
    
    @inst_name.setter
    def inst_name(self, value):
        self._inst_name = value
