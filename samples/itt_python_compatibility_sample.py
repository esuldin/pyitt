#!/usr/bin/env python
import pyitt.compatibility_layers.itt_python as itt

# pylint: disable=C0411
from argparse import ArgumentParser
from vtune_tool import run_vtune_hotspot_collection
from workload import workload


def run_sample():
    domain = itt.domain_create('my domain')
    itt.task_begin(domain, 'my task 1')
    workload()
    itt.task_end(domain)

    itt.pause()
    itt.task_begin(domain, 'paused task')
    workload()
    itt.task_end(domain)
    itt.resume()

    itt.task_begin(domain, 'my task 2')
    workload()
    itt.task_end(domain)


if __name__ == '__main__':
    parser = ArgumentParser(description='The sample that demonstrates the use of wrappers for the Task API.')
    parser.add_argument('--run-sample',
                        help='Runs code that uses wrappers for the Task API.',
                        action='store_true')
    args = parser.parse_args()

    if args.run_sample:
        run_sample()
    else:
        run_vtune_hotspot_collection(['python', __file__, '--run-sample'])
