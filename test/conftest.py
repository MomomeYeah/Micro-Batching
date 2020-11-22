import os
import pytest
import sys

# add root directory to path so that we can import from batcher module
TEST_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(TEST_DIR)
#PACKAGE_DIR = os.path.join(ROOT_DIR, "batcher")
sys.path.append(ROOT_DIR)

from batcher.batch_controller import BatchController
from batcher.job import Job
from batcher.simple_batch_processor import SimpleBatchProcessor

@pytest.fixture
def job():
    return Job(job_fn=lambda: 2)

@pytest.fixture
def make_job():
    def _make_job():
        return Job(job_fn=lambda: 2)

    yield _make_job

@pytest.fixture
def job_result(job: Job):
    return JobResult(job=job)

@pytest.fixture
def make_job_result(make_job):
    def _make_job_result():
        return JobResult(job=make_job())

    yield _make_job_result

@pytest.fixture
def batch_processor():
    return SimpleBatchProcessor()

@pytest.fixture
def make_batch_controller(batch_processor):
    controllers = []

    def _make_batch_controller(batch_size, batch_interval):
        return BatchController(
            batch_size=batch_size, batch_interval=batch_interval, batch_processor=batch_processor)

    yield _make_batch_controller

    # shutdown all controllers
    for controller in controllers:
        print ("Shutting down controller")
        controller.shutdown()
