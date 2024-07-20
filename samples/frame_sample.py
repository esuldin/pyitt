#!/usr/bin/env python
import pyitt

# pylint: disable=C0411
from argparse import ArgumentParser
from vtune_tool import run_vtune_hotspot_collection
from workload import workload


def run_sample():
    # pyitt.frame can be used as decorator
    @pyitt.frame
    def my_function_1():
        workload()

    # the list of arguments can be empty
    @pyitt.frame()
    def my_function_2():
        workload()

    # or you can specify the domain of the frame and other parameters
    @pyitt.frame(domain='my domain')
    def my_function_3():
        workload()

    # also, pyitt.frame can be used as a context manager
    with pyitt.frame():
        workload()
    # in this form you also can specify the name, the domain and other parameters in the same way
    with pyitt.frame(domain='my domain'):
        workload()

    my_function_1()
    my_function_2()
    my_function_3()

    # example for overlapped frames,
    # please note that nested/overlapping frames for the same domain are not allowed,
    # it is a limitation of native ITT API
    overlapped_frame_1 = pyitt.frame(domain='my domain 1')
    overlapped_frame_1.begin()
    workload()
    overlapped_frame_2 = pyitt.frame(domain='my domain 2')
    overlapped_frame_2.begin()
    workload()
    overlapped_frame_1.end()
    workload()
    overlapped_frame_2.end()

    # example with callable object
    class CallableClass:
        def __call__(self, *args, **kwargs):  # pylint: disable=W0621
            workload()

    callable_object = pyitt.frame(CallableClass())
    callable_object()


if __name__ == '__main__':
    parser = ArgumentParser(description='The sample that demonstrates the use of wrappers for the Frame API.')
    parser.add_argument('--run-sample',
                        help='Runs code that uses wrappers for the Frame API.',
                        action='store_true')
    args = parser.parse_args()

    if args.run_sample:
        run_sample()
    else:
        run_vtune_hotspot_collection(['python', __file__, '--run-sample'])
