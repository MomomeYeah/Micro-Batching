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

## Running the Sample Program with Vagrant

The sample program `micro_batching.py` demonstrates an example usage of the library.

If you have Vagrant installed, the easiest way to run this sample program would be:

* `vagrant up` - provision an Ubuntu 20.04 VM
* `vagrant ssh` - SSH into the newly-created VM
* `cd /vagrant` - go to the Vagrant working directory
* `python3 micro_batching.py ` - use `--help` for commandline options

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
* `BatchProcessor` must implement `BatchProcessorInterface`, and can be provided by
  the caller. This code defines `SimpleBatchProcessor` for testing purposes, and as
  an implementation example

## TODO Items

* implement full set of tests
* it would be nicer to use events to detect when `JobResults` are ready, so that
  a sleep-and-check loop isn't necessary
