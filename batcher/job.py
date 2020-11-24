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

    def complete(self) -> None:
        self.logger.debug("Running {}".format(self.job))
        try:
            self.result = self.job.job_fn()
        except Exception as e:
            self.error = True
            self.error_message = str(e)

    async def get_result(self) -> Any:
        self.logger.debug("Awaiting completion for {}".format(self.job))
        while True:
            await asyncio.sleep(1)

            if self.result or self.error:
                self.logger.debug("{} result ready!".format(self.job))
                break

        return self.result
