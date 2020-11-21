import pytest

from job import Job, JobResult

def test_create_job_result_without_job():
    """Test that JobResults cannot be created without jobs"""
    with pytest.raises(TypeError):
        job_result = JobResult()

def test_create_job_result_with_invalid_job():
    """Test that JobResults must be created with a valid Job"""
    with pytest.raises(ValueError):
        job_result = JobResult(job="job")

def test_create_job_result(job):
    """Test that JobResults can be created"""
    # create a job result, and make sure its result is None
    job_result = JobResult(job=job)
    assert job_result.result is None

    # complete the job, and make sure its result is correct
    job_result.complete()
    assert job_result.result == job_result.job.job_fn()
