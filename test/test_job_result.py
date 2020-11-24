import pytest

from batcher.job import Job, JobResult

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
    assert job_result.error == False
    assert job_result.error_message is None

    # set a positive result, and make sure its job is updated correctly
    job_result.set_result(result="result")
    assert job_result.result == "result"
    assert job_result.error == False
    assert job_result.error_message is None

    # set an error result, and make sure its job is updated correctly
    job_result.set_result(result=Exception("result"))
    assert job_result.result is None
    assert job_result.error == True
    assert job_result.error_message == "result"
