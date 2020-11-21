import asyncio


class SimpleBatchProcessor:
    def __init__(self):
        pass

    def process_jobs(self, jobs):
        print ("Processing jobs")
        for job in jobs:
            job.complete()
            print ("{} done".format(job.job))

        return True
