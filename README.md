# Micro-Batching

## Requirements

* expose a method which accepts a single `Job` and returns a `JobResult`
* process accepted `Jobs` in batches using a `BatchProcessor`
* Don't implement `BatchProcessor` - this should be a dependency of the library
* the maximum batch size should be configurable
* the maximum time between calls made to `BatchProcessor` should be configurable
* expose a shutdown method which returns after all previously accepted `Jobs` are processed

## Looking For

* well designed, production-ready code
* good documentation / comments
* a well written, maintainable test suite

## Running the Program with Vagrant

If you have Vagrant installed, the easiest way to run this program would be:

* `vagrant up` - provision an Ubuntu 20.04 VM
* `vagrant ssh` - SSH into the newly-created VM
* `cd /vagrant` - go to the Vagrant working directory
* `python3 job_runner.py ` - use `--help` for commandline options

## Running Tests

* Run `python3 -m pytest` from either the root directory, or within the `test` directory

## Assumptions

* A `Job` is created with a executable function, which will be executed when the
  `Job` is processed as part of a batch
* `JobResult` should return immediately, and have an async function which will return
  whenever the actual result has finished processing
* batches will be processed at most every `batch_interval` seconds
* if `batch_size` jobs exist at any point, then batch will be processed immediately
  without resetting the `batch_interval` loop

## Thoughts

* if we can't implement `BatchProcessor` then we'll have to mock it, presumably?
* https://stackoverflow.com/questions/43325501/how-do-i-write-a-sequence-of-promises-in-python
