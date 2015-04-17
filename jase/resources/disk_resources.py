import os, sys
import shutil
import time
import logging

from .resources import Request, ResourceManager, ResourceTimeoutError

class DiskRequest(Request):
    def __init__(self, size=None, job=None, subdirs=None):
        assert job is not None
        super().__init__(job=job)
        self.size = size
        self.subdirs = subdirs

class DiskResource:
    def __init__(self, path, mgr, size=0):
        self.path = path
        self.mgr = mgr
        self.size=size

        try:
            if os.path.exists(self.path) and not os.listdir(self.path) == "":
                shutil.rmtree(self.path)
            os.makedirs(self.path, exist_ok=True)
        except PermissionError:
            "http://bugs.python.org/issue14252"
            raise

    def __enter__(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path, exist_ok=False)

    def __exit__(self, type, value, traceback):
        if type is None:
            self.clean()

    def clean(self):
        os.removedirs(self.path)
        self.mgr.delete_resource(self)

class DiskManager(ResourceManager):
    """A generic resource for disk space.
    """
    log_name = "Disk"

    def __init__(self, root=".", max_size=None, polling_time=.01, log_file="disk_mgr.log"):

        root = os.path.abspath(root)
        if log_file:
            log_file = os.path.join(root, log_file)

        if not os.path.exists(root):
            raise FileNotFoundError("Root directory, {} does not exist.")

        super().__init__(polling_time=polling_time, log_file=log_file)

        self.info("Disk manager started on {}. Max size: {}".format(root, max_size))
        self.info("Polling time is {} seconds".format(self.polling_time))

        self.root = root
        self.max_size = max_size

class LocalDiskManager(DiskManager):
    """ A disk manager that just gives out directories
    """

    def request(self, job=None, size=0, timeout=None, subdirs=None):
        """
        :param name: The name of the job requesting the disk.  Used to create a subdirectory.
        :param size: Size of the space requested. (Optional).
        :return:
        """

        request = DiskRequest(job=job, size=size, subdirs=subdirs)
        self.info("Disk requested: {}, dirs={}, size={}".format(job.name, subdirs, size))
        resource = self.enqueue_request(request, timeout=timeout)
        return resource

    def get_resource(self, request):
        """ Called by the Resource base class to get a resource.  This method is responsible
        for allocating resources given the request.  If the resource is not available, it should
        block until the resource is available.

        This method should check for resource availability once every 'polling_time' seconds.
        """
        # If there is enough disk space for the requested job, grant the request.
        while self._running:
            if self.max_size is not None:
                available_space = sum([r.size for r in self.resources]) - self.max_size
            else:
                available_space = shutil.disk_usage(self.root).free

            if (request.size < available_space):
                if request.subdirs is not None:
                    subdirs = request.subdirs
                else:
                    subdirs = [request.name]
                job_dir = os.path.join(self.root, *subdirs)

                resource = DiskResource(path=job_dir, mgr=self, size=request.size)
                self.info("Disk granted to {}".format(job_dir))
                self.resources.append(resource)
                return resource
            else:
                self.info("Waiting for more disk space")
                time.sleep(self.polling_time)