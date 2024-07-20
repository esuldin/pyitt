#!/usr/bin/env python
import pyitt

# pylint: disable=C0411
from argparse import ArgumentParser
from vtune_tool import run_vtune_hotspot_collection
from workload import workload


def run_sample():
    # pyitt.pt_region can be used as decorator
    @pyitt.pt_region
    def my_function_1():
        workload()

    # the list of arguments can be empty
    @pyitt.pt_region()
    def my_function_2():
        workload()

    # or you can directly specify the name of the region
    @pyitt.pt_region('my function 3')
    def my_function_3():
        workload()

    # also, an object that is returned by pyitt.pt_region can be used as a context manager
    region_with_auto_name = pyitt.pt_region()
    for _ in range(5):
        with region_with_auto_name:
            workload()

    for _ in range(5):
        my_function_1()
    for _ in range(5):
        my_function_2()
    for _ in range(5):
        my_function_3()

    # example with callable object
    class CallableClass:
        def __call__(self, *args, **kwargs):  # pylint: disable=W0621
            workload()

    callable_object = pyitt.pt_region(CallableClass())
    for _ in range(5):
        callable_object()


if __name__ == '__main__':
    parser = ArgumentParser(description='The sample that demonstrates the use of wrappers for the PT API.')
    parser.add_argument('--run-sample',
                        help='Runs code that uses wrappers for the PT API.',
                        action='store_true')
    args = parser.parse_args()

    if args.run_sample:
        run_sample()
    else:
        run_vtune_hotspot_collection(['python', __file__, '--run-sample'])
