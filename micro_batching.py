import argparse
import asyncio
import logging
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
    parser.add_argument("--verbose", action="store_true", help = "Whether to use verbose logging")

    return parser.parse_args()


async def main(logger: logging.Logger, controller: BatchController):
    results=[]
    for i in range(3):
        logger.info ("Adding new job")
        # capture current value of loop variable here by using default value

        def job_fn(x = i):
            return x + 2
        job = Job(job_fn)
        results.append(controller.add_job(job))
        logger.info ("Added {}".format(job))
    logger.info ("All jobs added")

    logger.info ("Waiting for job results to be ready")
    await asyncio.gather(*[result.get_result() for result in results])
    for result in results:
        if result.error:
            logger.error ("{} failed with error {}".format(result, result.error_message))
        else:
            logger.info ("Result for {} is {}".format(result, result.result))


if __name__ == "__main__":
    controller=None
    try:
        args=parse_args()

        # create logger
        log_level = logging.DEBUG if args.verbose else logging.INFO
        logger = logging.getLogger("MicroBatching")
        logger.setLevel(log_level)

        # create console logging handler and add formatter
        ch = logging.StreamHandler()
        log_formatter = logging.Formatter("[%(levelname)8s] - %(message)s")
        ch.setFormatter(log_formatter)
        logger.addHandler(ch)
        logger.propagate = False

        # create batch controller
        processor=SimpleBatchProcessor()
        controller=BatchController(
            batch_size=args.batch_size, batch_interval=args.batch_interval, batch_processor=processor)

        # run main loop
        asyncio.run(main(logger=logger, controller=controller))

        # sleep for a while and run again
        time.sleep(15)
        asyncio.run(main(logger=logger, controller=controller))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error ("Exception: {}".format(e))
    finally:
        if controller is not None:
            controller.shutdown()
