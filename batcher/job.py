import asyncio
from typing import Callable


class Job:
    counter = 1

    def __init__(self, job_fn: Callable):
        if not isinstance(job_fn, Callable):
            raise ValueError("Job function must implement Callable")

        self.job_fn = job_fn
        self.job_id = Job.counter
        Job.counter += 1

    def __str__(self) -> str:
        return "Job {}".format(self.job_id)


class JobResult:
    def __init__(self, job: Job):
        if not isinstance(job, Job):
            raise ValueError("JobResult target must be a Job")

        self.job = job
        self.result = None

    def __str__(self) -> str:
        return "{}".format(self.job)

    def complete(self) -> None:
        print ("Running {}".format(self.job))
        self.result = self.job.job_fn()

    # TODO: catch exceptions?
    # TODO: nicer to use event here, but doesn't seem to want to work...
    async def get_result(self):
        print ("Awaiting completion for {}".format(self.job))
        while True:
            await asyncio.sleep(1)

            if self.result:
                print ("{} result ready!".format(self.job))
                break

        return self.result
