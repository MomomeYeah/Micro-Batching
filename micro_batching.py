import argparse
import asyncio
import os
import sys
import time

# add root directory to path so that we can import from batcher module
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
PACKAGE_DIR = os.path.join(ROOT_DIR, "batcher")
sys.path.append(ROOT_DIR)

from batcher.batch_controller import BatchController, SimpleBatchProcessor
from batcher.job import Job


def parse_args():
    parser=argparse.ArgumentParser(description = "Micro-Batching")
    parser.add_argument("--batch-size", required = False, default = 10, type = int,
                        help = "The maximum number of jobs to accept before forcing processing")
    parser.add_argument("--batch-interval", required = False, default = 10, type = int,
                        help = "The maximum amount of time in seconds to wait before processing")

    return parser.parse_args()


async def main(controller: BatchController):
    results=[]
    for i in range(3):
        print ("Adding new job")
        # capture current value of loop variable here by using default value

        def job_fn(x = i):
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
    controller=None
    try:
        args=parse_args()
        batch_size=args.batch_size
        batch_interval=args.batch_interval

        processor=SimpleBatchProcessor()
        controller=BatchController(
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
        if controller is not None:
            controller.shutdown()
