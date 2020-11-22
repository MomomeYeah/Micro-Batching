import os
import pytest
import sys

# add root directory to path so that we can import from batcher module
TEST_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(TEST_DIR)
#PACKAGE_DIR = os.path.join(ROOT_DIR, "batcher")
sys.path.append(ROOT_DIR)

from batcher.job import Job
from batcher.simple_batch_processor import SimpleBatchProcessor

@pytest.fixture
def job():
    return Job(job_fn=lambda: 2)

@pytest.fixture
def job_result(job: Job):
    return JobResult(job=job)

@pytest.fixture
def batch_processor():
    return SimpleBatchProcessor()
