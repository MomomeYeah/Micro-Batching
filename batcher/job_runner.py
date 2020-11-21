import asyncio
import threading
import time
from collections import deque
from typing import Callable

from args import parse_args
from job import Job, JobResult
from processor_interface import BatchProcessorInterface
from simple_batch_processor import SimpleBatchProcessor


class BatchControllerLoop(threading.Thread):
    def __init__(self, interval: int, invokable: Callable):
        self.interval = interval
        self.invokable = invokable
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while not self.stopped():
            print ("Worker thread sleeping for {} seconds".format(self.interval))
            self._stop.wait(self.interval)
            if self.stopped():
                print ("Worker thread done")
                continue
            print ("Worker thread invoking task")
            self.invokable()


class BatchController:
    def __init__(self, batch_size: int, batch_interval: int, batch_processor: BatchProcessorInterface):
        # how big to allow the job queue to get before processing batch
        self.batch_size = batch_size

        # max time to wait before processing batch
        self.batch_interval = batch_interval

        # batch processor object that will process a set of jobs
        self.batch_processor = batch_processor

        # set when shutting down
        self.shutting_down = False

        # the job queue
        self.jobs = deque()

        # batch interval thread
        self.loop = BatchControllerLoop(interval=self.batch_interval, invokable=self.process_jobs)
        self.process_thread = threading.Thread(target=self.loop.run)
        self.process_thread.start()

    def add_job(self, job: Job):
        """Add a job to the job queue, returning a job result"""
        # if shutting down, just return
        if self.shutting_down:
            return None

        # otherwise, add job to queue and return result object
        result = JobResult(job=job)
        self.jobs.append(result)

        # if we've hit the max batch size, then process now
        if len(self.jobs) >= self.batch_size:
            print ("Main thread has {} jobs, processing now".format(len(self.jobs)))
            self.process_jobs()

        return result

    def process_jobs(self, process_all: bool=False):
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

    def shutdown(self):
        """Exit after all jobs have been processed"""
        print ("Shutting down...")
        # mark ourselves as shutting down, so that no new jobs are accepted
        self.shutting_down = True
        print ("Processing all remaining jobs...")
        # process all remaining jobs
        self.process_jobs(process_all=True)
        print ("Terminating worker thread...")
        # once done, stop the looping interval processor and end the thread
        self.loop.stop()
        self.process_thread.join()
        print ("Shutdown process complete")


async def main(controller):
    results = []
    for i in range(3):
        print ("Adding new job")
        # capture current value of loop variable here by using default value

        def job_fn(x=i):
            return x + 2
        job = Job(job_fn)
        results.append(controller.add_job(job))
        print ("Added {}".format(job))
    print ("All jobs added")

    print ("Waiting for job results to be ready")
    await asyncio.gather(*[result.get_result() for result in results])
    for result in results:
        if result.error:
            print ("{} failed with error {}".format(result, result.error_message))
        else:
            print ("Result for {} is {}".format(result, result.result))


if __name__ == "__main__":
    try:
        args = parse_args()
        batch_size = args.batch_size
        batch_interval = args.batch_interval

        processor = SimpleBatchProcessor()
        controller = BatchController(
            batch_size=batch_size, batch_interval=batch_interval, batch_processor=processor)

        # run main loop
        asyncio.run(main(controller=controller))

        # sleep for a while and run again
        time.sleep(15)
        asyncio.run(main(controller=controller))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print ("Exception: {}".format(e))
    finally:
        controller.shutdown()
