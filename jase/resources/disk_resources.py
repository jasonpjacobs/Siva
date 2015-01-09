import os
import shutil
import time

from .resources import Request, ResourceManager, ResourceTimeoutError

class DiskRequest(Request):
    def __init__(self, size=None, job=None):
        assert job is not None
        super().__init__(job=job)
        self.size = size

class DiskResource:
    def __init__(self, path, mgr, size=0):
        self.path = path
        self.mgr = mgr
        self.size=size

    def __enter__(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def __exit__(self, type, value, traceback):
        if type is None:
            shutil.rmtree(self.path)
            self.mgr.delete_resource(self)

class DiskManager(ResourceManager):
    """A generic resource for disk space.
    """

    def __init__(self, root=".", max_size=None, polling_time=1):
        super().__init__(polling_time=polling_time)

        root = os.path.abspath(root)
        if not os.path.exists(root):
            raise FileNotFoundError("Root directory, {} does not exist.")

        self.root = root
        self.max_size = max_size


class LocalDiskManager(DiskManager):
    """ A disk manager that just gives out directories
    """

    def request(self, job=None, size=0, timeout=None):
        """
        :param name: The name of the job requesting the disk.  Used to create a subdirectory.
        :param size: Size of the space requested. (Optional).
        :return:
        """

        request = DiskRequest(job=job, size=size)
        resource = self.enqueue_request(request, timeout=timeout)
        return resource

    def get_resource(self, request):
        # If there is enough disk space for the requested job, grant the request.
        while self._run:
            if self.max_size is not None:
                available_space = sum([r.size for r in self.resources]) - self.max_size
            else:
                available_space = shutil.disk_usage(self.root).free

            if (request.size < available_space):
                subdir_name = request.name
                job_dir = os.path.join(self.root, subdir_name)
                resource = DiskResource(path=job_dir, mgr=self, size=request.size)
                self.resources.append(resource)
                return resource
            print("Waiting for disk space")
            time.sleep(self.polling_time)





