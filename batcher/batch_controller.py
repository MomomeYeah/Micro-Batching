import logging
import threading
from collections import deque
from typing import Callable

from .job import Job, JobResult
from .processor_interface import BatchProcessorInterface
from .simple_batch_processor import SimpleBatchProcessor


class BatchControllerLoop(threading.Thread):
    def __init__(self, interval: int, invokable: Callable) -> None:
        self.interval = interval
        self.invokable = invokable
        self._stop = threading.Event()

        self.logger = logging.getLogger("MicroBatching")

    def stop(self) -> None:
        self._stop.set()

    def stopped(self) -> bool:
        return self._stop.isSet()

    def running(self) -> bool:
        return not self.stopped()

    def run(self) -> None:
        while not self.stopped():
            self.logger.debug("Worker thread sleeping for {} seconds".format(self.interval))
            self._stop.wait(self.interval)
            if self.stopped():
                self.logger.debug("Worker thread done")
                continue
            self.logger.debug("Worker thread invoking task")
            self.invokable()


class BatchController:
    def __init__(self, batch_size: int, batch_interval: int, batch_processor: BatchProcessorInterface) -> None:
        # how big to allow the job queue to get before processing batch
        if not isinstance(batch_size, int):
            raise ValueError("Batch size must be an integer")
        self.batch_size = batch_size

        # max time to wait before processing batch
        if not isinstance(batch_interval, int):
            raise ValueError("Batch interval must be an integer")
        self.batch_interval = batch_interval

        # batch processor object that will process a set of jobs
        if not isinstance(batch_processor, BatchProcessorInterface):
            raise ValueError("Batch processor must implement BatchProcessorInterface")
        self.batch_processor = batch_processor

        # set when shutting down
        self.shutting_down = False

        # the job queue
        self.jobs = deque()

        # set logger
        self.logger = logging.getLogger("MicroBatching")

        # batch interval thread
        self.loop = BatchControllerLoop(interval=self.batch_interval, invokable=self.process_jobs)
        self.process_thread = threading.Thread(target=self.loop.run)
        self.process_thread.start()

    def add_job(self, job: Job) -> JobResult:
        """Add a job to the job queue, returning a job result"""
        # if shutting down, just return
        if self.shutting_down:
            return None

        # otherwise, add job to queue and return result object. Note that we
        # rely on JobResult to validate the input job
        result = JobResult(job=job)
        self.jobs.append(result)

        # if we've hit the max batch size, then process now
        if len(self.jobs) >= self.batch_size:
            self.logger.debug("Main thread has {} jobs, processing now".format(len(self.jobs)))
            self.process_jobs()

        return result

    def process_jobs(self, process_all: bool = False) -> None:
        jobs = []

        # in a loop, pop jobs from the queue until we have enough to process.
        # doing it this way means that we can still add jobs to end of the
        # queue without having to worry about contention
        processed = 0
        while True:
            # if no jobs left in the queue, we're done
            if not self.jobs:
                break

            # if we've hit the batch size, we're done unless we're
            # processing all remaining
            if processed == self.batch_size and not process_all:
                break

            # otherwise, pop a job from the queue
            jobs.append(self.jobs.popleft())

        # process the jobs
        self.batch_processor.process(jobs)

    def shutdown(self) -> None:
        """Exit after all jobs have been processed"""
        self.logger.debug("Shutting down...")
        # mark ourselves as shutting down, so that no new jobs are accepted
        self.shutting_down = True
        self.logger.debug("Processing all remaining jobs...")
        # process all remaining jobs
        self.process_jobs(process_all=True)
        self.logger.debug("Terminating worker thread...")
        # once done, stop the looping interval processor and end the thread
        self.loop.stop()
        self.process_thread.join()
        self.logger.debug("Shutdown process complete")
