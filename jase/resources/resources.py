import threading
import time
import os
import shutil
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

class ResourceManager(threading.Thread):
    def __init__(self, polling_time=1):
        super().__init__()
        # Queue to store incoming requests
        self.queue = Queue()

        # Initial state of the manager
        self._run = False

        # How often the request queue is polled for new requests (in seconds)
        self.polling_time = polling_time

        # Keep track of allocated resources
        self.resources = []

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
        if not self._started.is_set():
            self.start()
        self.queue.put(request)
        request.wait(timeout)

        # Check to see if the request timed out
        if request.resource is None:
            raise ResourceTimeoutError

        return request.resource

    def run(self):
        self._run = True
        while self._run is True:
            time.sleep(self.polling_time)
            self.process_requests()

    def process_requests(self):
        """ Simple processing loop that gets requests from the queue and waits for the resource to
        become available before granting.

        More sophisticated managers can override this method to implement prioritization, or allow
        smaller requests to get access to resources before larger ones.
        """
        while not self.queue.empty():
            request = self.queue.get()
            request.resource = self.get_resource(request)
            request.set()
        self.stop()

    def stop(self):
        super()._stop()
        self._run = False

    def get_resource(self, request):
        """ Called by the Resource base class to get a resource.  This method is responsible
        for allocating resources given the request.  If the resource is not available, it should
        block until the resource is available.

        This method should check for resource availability once every 'polling_time' seconds.
        """
        raise NotImplementedError

    def delete_resource(self, resource):
        self.resources.remove(resource)




