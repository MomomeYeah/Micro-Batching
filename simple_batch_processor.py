import asyncio


class SimpleBatchProcessor:
    def __init__(self):
        pass

    def process_jobs(self, jobs):
        print ("Processing jobs")
        for index, job in enumerate(jobs):
            job.complete()

            print ("Job {} done".format(index))

        return True
