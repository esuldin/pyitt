#!/usr/bin/env python
import pyitt

from argparse import ArgumentParser
from vtune_tool import run_vtune_hotspot_collection
from workload import workload
from threading import Thread


def run_sample():
    @pyitt.task
    def run_workload():
        workload()

    def thread_func(name: str):
        pyitt.thread_set_name(name)
        run_workload()

    threads = [Thread(target=thread_func, args=(f'Thread for iteration {i}',)) for i in range(4)]
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]


if __name__ == '__main__':
    parser = ArgumentParser(
        description='The sample that demonstrates the use of wrappers for the Thread Naming API.'
    )
    parser.add_argument('--run-sample',
                        help='Runs code that uses wrappers for Thread Naming API.',
                        action='store_true')
    args = parser.parse_args()

    if args.run_sample:
        run_sample()
    else:
        run_vtune_hotspot_collection(['python', __file__, '--run-sample'])
