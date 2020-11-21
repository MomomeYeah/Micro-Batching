import pytest
from job_runner import Job

def test_create_job_without_job_fn():
    """Test that Jobs cannot be created without functions"""
    with pytest.raises(TypeError):
        job = Job()

def test_create_job():
    """Test that Jobs can be created"""
    job_fn = lambda: None

    # create a job, and make sure its ID is 1
    job1 = Job(job_fn = job_fn)
    assert job1.job_id == 1

    # create another one, and make sure its ID is 2
    job2 = Job(job_fn = job_fn)
    assert job2.job_id == 2
