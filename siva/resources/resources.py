import threading
import time
import os
import sys
import shutil
import logging

from queue import Queue

class ResourceTimeoutError(TimeoutError):
    pass

class Request(threading.Event):
    """A class that describes a resource request.

    Subclassed from Event, so the requester can call the wait() method
    and block execution until the request is granted.
    """
    def __init__(self, job=None):
        super().__init__()
        self.job = job
        if hasattr(job,'name'):
            self.name = job.name
        else:
            self.name = ''

        self.resource = None

    def __repr__(self):
        return "{}(job={})".format(self.__class__.__name__, str(self.job))

class ResourceManager(threading.Thread):
    log_name = "Unnamed Resource Manager"

    def __init__(self, polling_time=1, log_file=None):
        super().__init__()
        # Queue to store incoming requests
        self.queue = Queue()

        # Initial state of the manager
        self._running = False

        # How often the request queue is polled for new requests (in seconds)
        self.polling_time = polling_time

        # Keep track of allocated resources
        self.resources = []

        # Logging
        self.setup_logging(log_file=log_file, log_name=self.log_name)

    def request(self, job, timeout=None):
        """ Called by the job dispatcher to request a resource.  The execution of this method is
          blocked until the resource is granted, or timed out.

        Resource specific managers can re-implement this method to modify the specific Resource class
        used for the request or to provide additional constraints or parameters.
        """

        request = Request(job=job)
        resource = self.enqueue_request(request, timeout=timeout)
        return resource

    def enqueue_request(self, request, timeout=None):
        """Places the request in the queue and waits for it to be granted.
        """
        if not self._running:
            self.start()
        self.queue.put(request)
        # The wait method will not return until the process_request loop
        # has called the request's set() method.
        if not request.wait(timeout):
            raise ResourceTimeoutError

        return request.resource

    def run(self):
        """Executes the resource manager.  This method is called in its own thread of execution
        when the start method is called.
        """
        self._running = True
        self.info("Resource manager started.".format(self.log_name))
        while self._running:
            time.sleep(self.polling_time)
            self.process_requests()
        self.debug('Run method is now halting.')

    def stop(self):
        self._running = False

    def process_requests(self):
        """ Simple processing loop that gets requests from the queue and waits for the resource to
        become available before granting.

        More sophisticated managers can override this method to implement prioritization, or allow
        smaller requests to get access to resources before larger ones.
        """
        if not self.queue.empty():
            request = self.queue.get()
            self.debug("Making request: {}".format(request))
            # get_resource will block if the the requested resource
            # is not available
            request.resource = self.get_resource(request)
            self.debug("Request granted: {}".format(request))
            request.set()

    def get_resource(self, request):
        """ Called by the Resource base class to get a resource.  This method is responsible
        for allocating resources given the request.  If the resource is not available, it should
        block until the resource is available.

        This method should check for resource availability once every 'polling_time' seconds.
        """
        raise NotImplementedError

    def delete_resource(self, resource):
        self.resources.remove(resource)


    def setup_logging(self, log_file=None, log_name="Resource", level=logging.WARNING):
        if log_file is not None:
            self.logger = logging.getLogger(log_name)
            self.logger.setLevel(level)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

            fh = logging.FileHandler(log_file, mode='w')
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            self.logger.info("Local resource manager created at {}".format(log_file))
        else:
            self.logger = None

    def close(self):
        for handler in self.logger.handlers:
            if hasattr(handler, 'close'):
                handler.close()

    def debug(self, msg):
        if self.logger is not None:
            self.logger.debug(msg)

    def info(self, msg):
        if self.logger is not None:
            self.logger.info(msg)

    def warn(self, msg):
        if self.logger is not None:
            self.logger.warn(msg)

    def error(self, msg):
        if self.logger is not None:
            self.logger.error(msg)






