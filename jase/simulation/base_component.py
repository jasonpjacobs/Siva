from ..components import Component
from ..resources.disk_resources import LocalDiskManager
from ..simulation.table import Table

import logging
import threading
import sys
import os

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

class Error(Status):
    pass

class ExecutionError(Exception):
    '''An exception raised when a Component encounters a problem during execution'''

class BaseComponent(Component):
    """ Base class for all simulation components

    This class defines how each component is executed.
    """
    _registries = ["components", "params", "measurements"]

    def __init__(self, parent=None, children=None, name=None, params=None, measurements=None, work_dir=".",
                 log_file=None, disk_mgr=None, parallel=False):

        super().__init__(parent=parent, children=children, name=name)

        # If 'vars' was specified, we assume the procedural interface is being used to define the loop variables.
        # If the declarative interface is used, loop_vars will already be populated
        if params is not None:
            # Convert to list from dict, if needed
            if hasattr(params, 'values'):
                params = params.values()

            for param in params:
                param.register_from_inst(parent=self, name=param.name)

        if measurements is not None:
            if hasattr(measurements, 'values'):
                measurements = measurements.values()

            for measurement in measurements:
                measurement.register_from_inst(parent=self, name=measurement.name)
        else:
            if not hasattr(self, 'measurements'):
                self.measurements = {}


        self.work_dir = work_dir

        self.log_file = log_file
        self.logger = None

        self.disk_mgr = disk_mgr
        self.parallel = parallel

        self.status = Uninitialized

        self.master = self
        self.index = None

        self.lock = threading.RLock()

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
                    # "Once a thread object is created, its activity must be started by calling the 
                    # thread’s start() method. This invokes the run() method in a separate thread of control."
                    # 
                    # Our run method will then call execute(), then start each of the child components.
                    # When those finish running, our own measure() method will be called.
                    thread.start()  #--> self.run()
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
        """Called by a thread's start() method.
        """
        try:
            self.execute()
            for component in self.components.values():
                component.start(wait=True)
            self.measure()
        except ExecutionError:
            self.status = Error
            raise

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

        self.setup_work_area()

        with self.lock:
            if self is self.master:
                self.setup_logging()

        # Create a results table
        self.results = Table()

        self.status = Initialized

    def setup_work_area(self):

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

    def setup_logging(self):
        assert self.master is self
        if self.log_file is not None and self.logger is None:
            path = os.path.join(self.work_dir, self.log_file)

            self.logger = logging.getLogger(self.path)
            self.logger.setLevel(logging.DEBUG)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

            fh = logging.FileHandler(path, mode='w')
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            self.logger.info("Log file for {} created.".format(self.path))
            self.log_file = path
        else:
            self.logger = None
            self.log_file = None

    def measure(self):

        self.debug("{} ({}): Evaluating measurements".format(self.inst_name, id(self)))

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
        self.debug("  About to add results: {}".format(self.path))
        with self.lock:
            self.master.results.add_row(record, row=self.index)
            self.debug("  Results added.")
        self.status = Measured

    def final(self):
        self.status = Finalized
        self.info("Done.")

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
    def root(self):
        return super().root.master

    def __repr__(self):
        name = "{}(name={})".format(self.__class__.__name__, self.inst_name)
        return name

    def debug(self, msg):
        if self.logger is not None:
            with self.lock:
                self.master.logger.debug(msg)

    def info(self, msg):
        if self.logger is not None:
            with self.lock:
                self.master.logger.info(msg)

    def warn(self, msg):
        if self.logger is not None:
            with self.lock:
                self.logger.warn(msg)

    def error(self, msg):
        if self.logger is not None:
            with self.lock:
                self.logger.error(msg)

