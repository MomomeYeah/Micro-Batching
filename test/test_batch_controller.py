import asyncio
import pytest
from asyncio.exceptions import TimeoutError
from async_timeout import timeout
from datetime import datetime, timedelta

from batcher.batch_controller import BatchController


def test_create_controller_without_required_params(batch_processor):
    """Test that Controller cannot be created without required params"""

    # missing batch size
    with pytest.raises(TypeError):
        controller = BatchController(batch_interval=10, batch_processor=batch_processor)

    # missing batch interval
    with pytest.raises(TypeError):
        controller = BatchController(batch_size=10, batch_processor=batch_processor)

    # missing batch processor
    with pytest.raises(TypeError):
        controller = BatchController(batch_size=10, batch_interval=10)


def test_create_controller_with_invalid_params(batch_processor):
    """Test that Controller must be created with a valid params"""

    # invalid batch size
    with pytest.raises(ValueError):
        job_result = BatchController(
            batch_size="string", batch_interval=10, batch_processor=batch_processor)

    # invalid batch interval
    with pytest.raises(ValueError):
        job_result = BatchController(
            batch_size=10, batch_interval="string", batch_processor=batch_processor)

    # invalid batch processor
    with pytest.raises(ValueError):
        job_result = BatchController(
            batch_size=10, batch_interval=10, batch_processor="string")


def test_create_controller(batch_processor):
    """Test that Controller can be created"""
    controller = BatchController(
        batch_size=10, batch_interval=10, batch_processor=batch_processor)
    assert not controller.jobs

    # check that controller loop is running
    assert controller.loop.running()

    # call controller shutdown method and check loop no longer running
    controller.shutdown()
    assert controller.loop.stopped()


@pytest.mark.asyncio
async def test_controller_batch_size(batch_processor, make_job):
    """Test that jobs are executed according to batch size.

    We set a very long batch interval so we can wait a while and check that
    jobs aren't processed, then add the right number of jobs and check they
    are executed right away
    """
    try:
        controller = BatchController(
            batch_size=2, batch_interval=999, batch_processor=batch_processor)
        assert not controller.jobs

        # check that controller loop is running
        assert controller.loop.running()

        # add a job and check that it doesn't get run
        job_result_1 = controller.add_job(job=make_job())
        timeout_duration = 10
        with pytest.raises(TimeoutError), timeout(timeout_duration):
            await job_result_1.get_result()

        # add a second job and check that they both get run
        job_result_2 = controller.add_job(job=make_job())
        with timeout(timeout_duration):
            await asyncio.gather(job_result_1.get_result(), job_result_2.get_result())

        assert job_result_1.result is not None
        assert job_result_2.result is not None

    finally:
        controller.shutdown()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("batch_interval", [2, 5, 10])
    async def test_controller_batch_interval(batch_interval, batch_processor, job):
        """Test that jobs are executed according to batch interval.

        We expect to wait at most the length of the interval, plus an extra second
        to account for the polling rate of job results
        """
        try:
            controller = BatchController(
                batch_size=999, batch_interval=batch_interval, batch_processor=batch_processor)
            assert not controller.jobs

            # check that controller loop is running
            assert controller.loop.running()

            # check start time
            time_start = datetime.now()
            # add a job and wait for result
            job_result = controller.add_job(job=job)

            # set a timeout here just in case getting results hangs
            expected_max_duration = batch_interval + 1
            timeout_duration = expected_max_duration + 1
            with timeout(timeout_duration):
                await job_result.get_result()

            # check finish time
            time_finish = datetime.now()

            time_diff = (time_finish - time_start).seconds
            assert time_diff < expected_max_duration

        finally:
            controller.shutdown()
