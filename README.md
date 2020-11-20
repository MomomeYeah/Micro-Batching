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

## Thoughts

* if we can't implement `BatchProcessor` then we'll have to mock it, presumably?
* what should the interface for a `Job` be? A function?
* what should a `JobResult` look like? Return immediately and notify caller when done?
* do we process any time we hit either max batch size or interval?
* how does the batcher accept jobs? expose API?
* https://stackoverflow.com/questions/43325501/how-do-i-write-a-sequence-of-promises-in-python
