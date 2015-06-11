import pytest
import unittest
import os
import tempfile

class A(unittest.TestCase):
    pass

from ..disk_resources import DiskResource, LocalDiskManager


class Job:
    def __init__(self, name):
        self.name = name


@pytest.fixture
def work_dir():
    #return tempfile.mkdtemp()
    path = "p:\work\disk_text"
    if not os.path.exists(path):
        os.mkdir(path)
    return path

@pytest.fixture
def local_disk(work_dir):
    mgr = LocalDiskManager(root=work_dir)
    return mgr

def test_disk_creation(local_disk):
    mgr = local_disk
    job = Job(name='job1')

    disk = mgr.request(job)
    with disk:
        assert os.path.exists(disk.path)
        root, subdir = os.path.split(disk.path)
        assert subdir == 'job1'
        assert root == os.path.abspath(local_disk.root)
    assert os.path.exists(disk.path) is False

def test_disk_timeout(work_dir):
    mgr = LocalDiskManager(root=work_dir, max_size=0)
    job = Job(name='test')
    with pytest.raises(TimeoutError):
        disk = mgr.request(job, size=1e6, timeout=2)


def test_subdir_creation(work_dir):
    mgr = LocalDiskManager(root=work_dir)
    job = Job(name='test')
    disk = mgr.request(job, subdirs=['a','b','c'])
    if True:
        assert os.path.exists(disk.path)
        path = os.path.join(work_dir, *['a','b','c'])
        assert os.path.exists(path)


