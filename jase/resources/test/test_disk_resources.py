import pytest
import unittest
import os
class A(unittest.TestCase):
    pass

from ..disk_resources import DiskResource, LocalDiskManager


class Job:
    def __init__(self, name):
        self.name = name

def test_disk_creation():
    mgr = LocalDiskManager()
    job = Job(name='job1')

    disk = mgr.request(job)
    with disk:
        assert os.path.exists(disk.path)
        root, subdir = os.path.split(disk.path)
        assert subdir == 'job1'
        assert root == os.path.abspath('.')
    assert os.path.exists(disk.path) is False

def test_disk_timeout():

    mgr = LocalDiskManager(max_size=0)
    job = Job(name='test')
    with pytest.raises(TimeoutError):
        disk = mgr.request(job, size=1e6, timeout=2)
    mgr.stop()


