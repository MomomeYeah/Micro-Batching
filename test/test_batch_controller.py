import pytest

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
