from ..components import Component
from ..resources.disk_resources import LocalDiskManager
from ..simulation.table import Table

import logging
import threading
import sys
import os

import concurrent
from concurrent.futures import ThreadPoolExecutor

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

    num_threads = 100

    def __init__(self, parent=None, children=None, name=None, params=None, measurements=None, work_dir=None,
                 log_file=None, disk_mgr=None, parallel=False, log_severity=logging.INFO):

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

        self.lock = threading.RLock()

        self._work_dir = work_dir
        self._work_dir_resource = None

        self.log_file = log_file
        self.logger = None
        self.log_severity = log_severity

        self._disk_mgr = disk_mgr

        self.parallel = parallel
        self.status = Uninitialized

        self.master = self
        self.index = None

        self.results = Table()

        # Keep a list of files created by this component, to aid housecleaning
        self._files = []

    @property
    def disk_mgr(self):
        if self is not self.root:
            return self.root.disk_mgr

        if self._disk_mgr is None and self._work_dir is not None:
            try:
                self._disk_mgr = LocalDiskManager(root=self._work_dir)
            except OSError:
                raise
        return self._disk_mgr

    @disk_mgr.setter
    def disk_mgr(self, value):
        if self is self.root:
            self._disk_mgr = value

    def start(self, wait=True):
        """ Starts this component's portion of the analysis.
        """
        # Initialize:  Get disk space, logs, etc.
        self.initialize()

        # This component may spawn several variants to run in their own threads.  (E.g., loop iterations).
        # These lists will keep track of them.
        #self.threads = []
        self.variants = []
        self.futures = []

        if self.parallel is False:
            num_threads = 1
        else:
            num_threads = self.num_threads

        with ThreadPoolExecutor(max_workers=num_threads) as pool:
            for index, iteration in enumerate(self):

                self.variants.append(iteration)

                # Make sure variant knows who the master is, so they can report
                # results to the same location
                iteration.master = self

                # The variant should also know its index, so it
                # can add its results to the correct row in the results table
                iteration.index = index

                # Submit the job
                future = pool.submit(iteration.run)
                future.job = iteration
                self.futures.append(future)

            # Wait for all schedules jobs to complete
            if wait:
                for future in concurrent.futures.as_completed(self.futures):
                    if future.exception() is not None:
                        msg = future.result()
                        self.error("Problem running job: {}".format(msg))
                        future.job.status = Error(msg)
                    else:
                        self.info("Job {} completed".format(future.job.path))


        # Final clean up
        if wait and self.status is not Error:
            self.final()
            for variant in self.variants:
                if variant.status is not Error and variant is not self:
                    self.info("Cleaning up {}".format(variant.inst_name))
                    variant.clean()

        del self.variants
        del self.futures

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

    def wait(self):
        """Waits for all running threads to complete
        """
        raise NotImplementedError()
        """
        if self.threads is not None:
            for thread in self.threads:
                thread.join()
        """

    def initialize(self):
        """ The first step in a simulation.
        * Initialize local variables.
        * Creates local directories on the work disk.
        """

        self.setup_work_area()

        with self.lock:
            if self is self.root.master:
                self.setup_logging()
                self.info("Setting up logging")

        # Create a results table
        with self.lock:
            self.master.results = Table()

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
            resource = disk_mgr.request(job=self, subdirs=subdirs)
            self._work_dir_resource = resource
            self._work_dir = resource.path
            self.info("Got disk area: {}".format(self._work_dir))

    def setup_logging(self):
        assert self.root.master is self
        if self.log_file is not None and self.logger is None:
            path = os.path.join(self._work_dir, self.log_file)

            self.logger = logging.getLogger(self.path)
            self.logger.setLevel(self.log_severity)

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

    def close_logging(self):
        if self.log_file is not None and self.logger is not None:
            for handler in self.logger.handlers:
                if hasattr(handler, 'close'):
                    handler.close()

    def measure(self):

        self.info("{} ({}): Evaluating measurements".format(self.inst_name, id(self)))

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
        self.info("Creating summary: {}".format(self.path))
        self.summarize()

        for child in self.children:
            child.clean()
        self.results.close()
        self.info("{}: Done.".format(self.path))
        self.close_logging()

    def summarize(self):
        """ Called after all child processes are finished to
        aggregate and summarize the data.
        """
        pass

    def clean(self):
        """Clean up work area and file handles.  This is called by the parent after
        the final() method has been called.
        """
        if self.status is Error:
            return

        self.info("Cleaning up work area for {}".format(self.path))
        for file in self._files:
            try:
                os.remove(file)
            except OSError as e:
                self.error("Could not remove file: {} ({})".format(file, self.path))

        if self._work_dir_resource:
            self._work_dir_resource.clean()

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

    def clone(self, master=None, clone_inst=None, **kwargs):
        clone = super().clone(clone_inst=clone_inst, **kwargs)
        clone.master = master
        return clone

    @property
    def master(self):
        if self._master is None:
            return self
        else:
            return self._master

    @master.setter
    def master(self, value):
        self._master = value

    @property
    def editor(self):
        pass

    @property
    def root(self):
        return super().root.master

    @property
    def results(self):
        if self is self.master:
            return self._results
        else:
            return self.master.results

    @results.setter
    def results(self, value):
        self._results = value

    def __repr__(self):
        name = "{}(name={})".format(self.__class__.__name__, self.inst_name)
        return name


    @property
    def log_msg_prefix(self):
        return ". "*len(self.path_components)

    def debug(self, msg):
        if self.root.master.logger is not None:
            with self.root.master.lock:
                self.root.master.logger.debug(self.log_msg_prefix + msg)

    def info(self, msg):
        if self.root.master.logger is not None:
            with self.root.master.lock:
                self.root.master.logger.info(self.log_msg_prefix + msg)

    def warn(self, msg):
        if self.root.master.logger is not None:
            with self.root.master.lock:
                self.root.master.logger.warn(self.log_msg_prefix + msg)

    def error(self, msg):
        if self.root.master.logger is not None:
            with self.root.master.lock:
                self.root.master.logger.error(self.log_msg_prefix + msg)


class Root(BaseComponent):
    """ The root component for any analysis.  Contains resource managers, final results table.
    """

    pass