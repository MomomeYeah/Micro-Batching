from typing import List

from job import JobResult


class BatchProcessorInterface:
    def process(self, job_results: List[JobResult]) -> None:
        """Process all of the given JobResults"""
        pass
