from ..components import Component
from ..resources.disk_resources import LocalDiskManager
from ..simulation.table import Table

import logging
import threading
import h5py
import os

import collections

class Status:
    pass


class Uninitialized(Status):
    pass


class Initialized(Status):
    pass


class Running(Status):
    pass


class Measured(Status):
    pass


class Finalized(Status):
    pass


class BaseComponent(Component):
    """ Base class for all simulation components

    This class defines how each component is executed.
    """
    _registries = ["components", "params", "measurements"]

    def __init__(self, parent=None, children=None, name=None, params=None, measurements=None, work_dir=".",
                 log_file=None, disk_mgr=None, parallel=False):

        self._registries = ["components", "params", "measurements"]

        super().__init__(parent=parent, children=children, name=name)



        # If 'vars' was specified, we assume the procedural interface is being used to define the loop variables.
        # If the declarative interface is used, loop_vars will already be populated
        if params is not None:
            # Convert to list from dict, if needed
            if hasattr(params, 'values'):
                params = params.values()

            for param in params:
                param.register_from_inst(parent=self, name=param.name, cls=self.__class__)

        if measurements is not None:
            if hasattr(measurements, 'values'):
                measurements = measurements.values()

            for measurement in measurements:
                measurement.register_from_inst(parent=self, name=measurement.name, cls=self.__class__)


        self.work_dir = work_dir
        self.results = Table()

        self.log_file = log_file
        self.log = None

        self.disk_mgr = disk_mgr
        self.parallel = parallel

        self.status = Uninitialized

        self.master = self
        self.index = None

        self.lock = threading.Lock()

    @property
    def disk_mgr(self):
        if self._disk_mgr is None and self.work_dir is not None:
            return LocalDiskManager(root=self.work_dir)
        return self._disk_mgr

    @disk_mgr.setter
    def disk_mgr(self, value):
        self._disk_mgr = value

    def start(self, wait=True):
        """ Starts this component's portion of the analysis.
        """
        # Initialize:  Get disk space, logs, etc.
        self.initialize()

        # This component may spawn several variants to run in their own threads.  (E.g., loop iterations).
        # These lists will keep track of them.
        self.threads = []
        self.variants = []

        for index, iteration in enumerate(self):
            thread = threading.Thread(target=iteration.run)
            self.threads.append(thread)
            self.variants.append(iteration)

            # Make sure variant knows who the master is, so they can report
            # results to the same location
            iteration.master = self

            # The variant should also know its index, so it
            # can add its results to the correct row in the results table
            iteration.index = index

        # Execute the threads
        if len(self.threads) > 0:
            if self.parallel:
                for thread in self.threads:
                    thread.start()
                # Wait for all to finish
                if wait:
                    for thread in self.threads:
                        thread.join()
            else:
                for thread in self.threads:
                    thread.start()
                    thread.join()
        # Final clean up
        if wait:
            self.final()

    def run(self):
        """Called by a thread
        """
        self.execute()
        for component in self.components.values():
            component.start(wait=True)
        self.measure()

    def wait(self):
        """Waits for all running threads to complete
        """
        if self.threads is not None:
            for thread in self.threads:
                thread.join()

    def initialize(self):
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
        subdirs = [comp.inst_name for comp in self.path_components]

        if disk_mgr:
            request = disk_mgr.request(job=self, subdirs=subdirs)
            self.work_dir = request.path

        # Create a log file
        self.setup_logging()

        # Create a results table
        with self.lock:
            self.results = Table()

        self.status = Initialized

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

    def measure(self):
        if self.root.log:
            self.root.log.debug("{} ({}): Evaluating measurements".format(self.inst_name, id(self)))

        # Evaluate all measurement statements
        for m in self.measurements.values():
            m.evaluate(self.hierarchy_namespace)

        # Now record input variables and measurement values
        # into the results table
        record = {}
        record.update(self.hierarchy_params)

        # As well as the measured values
        for m in self.measurements.values():
            record[m.name] = m.value

        # Add it to the master's results table
        with self.lock:
            self.master.results.add_row(record, row=self.index)
        self.status = Measured

    def final(self):
        pass

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        # By default, just execute once
        if self._i > 0:
            raise StopIteration
        self._i += 1

        #return self.clone()
        return self

    @property
    def editor(self):
        pass

    @property
    def inst_name(self):
        if hasattr(self, '_inst_name') and self._inst_name is not None:
            return self._inst_name
        else:
            return self.name
    
    @inst_name.setter
    def inst_name(self, value):
        self._inst_name = value


    @property
    def root(self):
        return super().root.master



    def __repr__(self):
        name = "{}(name={})".format(self.__class__.__name__, self.inst_name)
        return name

