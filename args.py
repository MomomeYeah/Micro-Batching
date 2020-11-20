import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Micro-Batching")
    parser.add_argument("--batch-size", required=False, default=10, type=int,
                        help="The maximum number of jobs to accept before forcing processing")
    parser.add_argument("--batch-interval", required=False, default=10, type=int,
                        help="The maximum amount of time in seconds to wait before processing")

    return parser.parse_args()
