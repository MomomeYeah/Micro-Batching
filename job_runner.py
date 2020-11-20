import asyncio
import threading
import time
from args import parse_args
from simple_batch_processor import SimpleBatchProcessor


class JobResult:
    def __init__(self, job):
        if not isinstance(job, Job):
            raise Exception("Get a real job!")

        self.job = job
        self.event = asyncio.Event()
        self.result = None

    def complete(self):
        print ("Running job")
        self.result = self.job.job_fn()

        print ("Marking job as done")
        self.event.set()

    # TODO: catch exceptions?
    # TODO: nicer to use event here, but doesn't seem to want to work...
    async def get_result(self):
        print ("Job result waiting completion")
        while True:
            await asyncio.sleep(1)
            # await self.event.wait()

            if self.result:
                print ("Job result done!")
                break

        return self.result


class Job:
    def __init__(self, job_fn):
        self.job_fn = job_fn


class BatchControllerLoop(threading.Thread):
    def __init__(self, interval, invokable):
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
    def __init__(self, batch_size, batch_interval, batch_processor):
        # how big to allow the job queue to get before processing batch
        self.batch_size = batch_size

        # max time to wait before processing batch
        self.batch_interval = batch_interval

        # batch processor object that will process a set of jobs
        self.batch_processor = batch_processor

        # set when shutting down
        self.shutting_down = False

        # the job queue
        # TODO: collections.deque would be more efficient here
        self.jobs = []

        # main thread
        self.loop = BatchControllerLoop(interval=self.batch_interval, invokable=self.process_jobs)
        self.process_thread = threading.Thread(target=self.loop.run)
        self.process_thread.start()

    def add_job(self, job):
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

    def process_jobs(self, process_all=False):
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
            jobs.append(self.jobs.pop(0))

        # process the jobs
        self.batch_processor.process_jobs(jobs)

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
    def job_fn(x): return x + 2
    job1 = Job(lambda: job_fn(1))
    job2 = Job(lambda: job_fn(2))
    job3 = Job(lambda: job_fn(3))

    print ("Adding job 1")
    result1 = controller.add_job(job1)
    print ("Adding job 2")
    result2 = controller.add_job(job2)
    print ("Adding job 3")
    result3 = controller.add_job(job3)
    print ("Done")

    print ("Getting first result")
    await asyncio.gather(
        result1.get_result(), result2.get_result(), result3.get_result())
    print ("Result 1 is {}".format(result1.result))
    print ("Result 2 is {}".format(result1.result))
    print ("Result 3 is {}".format(result1.result))


if __name__ == "__main__":
    try:
        args = parse_args()
        batch_size = args.batch_size
        batch_interval = args.batch_interval

        processor = SimpleBatchProcessor()
        controller = BatchController(
            batch_size=batch_size, batch_interval=batch_interval, batch_processor=processor)

        asyncio.run(main(controller=controller))
    except KeyboardInterrupt:
        controller.shutdown()
    except Exception as e:
        print ("Exception: {}".format(e))
        controller.shutdown()
