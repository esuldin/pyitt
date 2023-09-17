#!/usr/bin/env python
import pyitt

from argparse import ArgumentParser
from vtune_tool import run_vtune_hotspot_collection
from workload import workload


def run_sample():
    @pyitt.active_region
    @pyitt.task
    def run_workload():
        workload()

    run_workload()

    for i in range(4):
        with pyitt.active_region(activator=lambda: i % 2):
            with pyitt.task(f'for loop iteration {i}'):
                workload()

    pyitt.collection_control.resume()

    with pyitt.task('resumed region'):
        workload()

    with pyitt.paused_region():
        with pyitt.task('paused region'):
            workload()


if __name__ == '__main__':
    parser = ArgumentParser(
        description='The sample that demonstrates the use of wrappers for the Collection Control API.'
    )
    parser.add_argument('--run-sample',
                        help='Runs code that uses wrappers for Collection Control API.',
                        action='store_true')
    args = parser.parse_args()

    if args.run_sample:
        run_sample()
    else:
        run_vtune_hotspot_collection(['python', __file__, '--run-sample'],
                                     ['-start-paused'])
