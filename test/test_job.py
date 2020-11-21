import pytest

from job import Job

def test_create_job_without_job_fn():
    """Test that Jobs cannot be created without functions"""
    with pytest.raises(TypeError):
        job = Job()

def test_create_job_with_invalid_fn():
    """Test that Jobs must be created with a valid function"""
    with pytest.raises(ValueError):
        job = Job(job_fn="job_fn")

def test_create_job():
    """Test that Jobs can be created"""
    job_fn = lambda: None

    # get current Job counter value
    job_id = Job.counter

    # create a job, and make sure its ID matches the class counter above
    job1 = Job(job_fn = job_fn)
    assert job1.job_id == job_id

    # create another one, and make sure its ID has been incremented
    job2 = Job(job_fn = job_fn)
    assert job2.job_id == job_id + 1
