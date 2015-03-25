import pytest
import time

from ..resources import ResourceManager, Request


class TestMgr(ResourceManager):
    log_name = "TestMgr"


    def __init__(self, polling_time=.01, log_file="TestMgr.log"):
        super().__init__(polling_time=.1, log_file=log_file)

        self.num_requests = 0
        self.num_reqests_processed = 0
        self.num_process_iterations = 0

    def request(self, job, timeout=None):
        self.num_requests += 1
        super().request(job, timeout=timeout)

    def process_requests(self):
        """Keeps track of the number of times
        the process request loop has been called
        """
        self.num_process_iterations += 1
        super().process_requests()

    def get_resource(self, request):
        time.sleep(.13)
        self.info("Num requests: {}".format(self.num_requests))
        return 'Fake resource:{}'.format(str(request.job))

@pytest.mark.skipif(False, reason='debug')
def test_polling():

    mgr = TestMgr(polling_time=0.1)
    assert mgr.num_process_iterations == 0

    time.sleep(.2)
    assert mgr.num_process_iterations == 0

    mgr.start()
    time.sleep(.5)
    assert mgr.num_process_iterations >= 4


def test_queueing():
    mgr = TestMgr(polling_time=.1, log_file=r'P:\work\test_resources\queue.log')

    assert mgr.num_requests == 0
    assert mgr.num_process_iterations == 0

    mgr.request(job="Req #1")
    mgr.request(job="Req #2")
    mgr.stop()

    assert mgr.num_process_iterations > 0
    assert mgr.num_requests == 2


