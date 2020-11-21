from typing import List

from job import JobResult
from processor_interface import BatchProcessorInterface


class SimpleBatchProcessor(BatchProcessorInterface):
    def process(self, job_results: List[JobResult]) -> None:
        print ("Processing job results")
        for job_result in job_results:
            job_result.complete()
            print ("{} done".format(job_result))
