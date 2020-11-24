import logging
from typing import List

from .job import JobResult
from .processor_interface import BatchProcessorInterface


class SimpleBatchProcessor(BatchProcessorInterface):
    def __init__(self) -> None:
        self.logger = logging.getLogger("MicroBatching")

    def process(self, job_results: List[JobResult]) -> None:
        self.logger.debug("Processing job results")
        for job_result in job_results:
            try:
                result = job_result.job.job_fn()
            except Exception as e:
                result = e

            job_result.set_result(result=result)
            self.logger.debug("{} done".format(job_result))
