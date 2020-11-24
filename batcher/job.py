import asyncio
import logging
from typing import Any, Callable


class Job:
    counter = 1

    def __init__(self, job_fn: Callable) -> None:
        if not isinstance(job_fn, Callable):
            raise ValueError("Job function must implement Callable")

        self.job_fn = job_fn
        self.job_id = Job.counter
        Job.counter += 1

    def __str__(self) -> str:
        return "Job {}".format(self.job_id)


class JobResult:
    def __init__(self, job: Job) -> None:
        if not isinstance(job, Job):
            raise ValueError("JobResult target must be a Job")

        self.job = job
        self.result = None
        self.error = False
        self.error_message = None

        self.logger = logging.getLogger("MicroBatching")

    def __str__(self) -> str:
        return "{}".format(self.job)

    def set_result(self, result: Any) -> None:
        """Set the results of a job.

        If the result is an Exception (or any subclass) then this will be marked
        as an error, and otherwise the actual result of the job will be set"""
        self.logger.debug("Setting result for {}".format(self.job))
        if isinstance(result, Exception):
            self.result = None
            self.error = True
            self.error_message = str(result)
        else:
            self.result = result
            self.error = False
            self.error_message = None

    async def get_result(self) -> Any:
        """Wait for Job to be processed, returning the result

        It would be nicer to use an asyncio.Event to mark completion here, to
        avoid needing to sleep loop."""
        self.logger.debug("Awaiting completion for {}".format(self.job))
        while True:
            await asyncio.sleep(1)

            if self.result or self.error:
                self.logger.debug("{} result ready!".format(self.job))
                break

        return self.result
