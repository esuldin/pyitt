#!/usr/bin/env python
import pyitt

# pylint: disable=C0411
from argparse import ArgumentParser
from asyncio import run, sleep, create_task
from vtune_tool import run_vtune_hotspot_collection
from workload import workload


def run_sync_functions():
    # pyitt.task can be used as decorator
    @pyitt.task
    def my_function_1():
        workload()

    # the list of arguments can be empty
    @pyitt.task()
    def my_function_2():
        workload()

    # or you can specify the name of the task and other parameters
    @pyitt.task('my function 3')
    def my_function_3():
        workload()

    # like domain
    @pyitt.task(domain='my domain')
    def my_function_4():
        workload()

    @pyitt.task
    @pyitt.task('my function 5')
    def my_function_5():
        workload()

    # also, pyitt.task can be used as a context manager
    with pyitt.task():
        workload()
    # in this form you also can specify the name, the domain and other parameters in the same way
    with pyitt.task('my task', 'my domain'):
        workload()

    my_function_1()
    my_function_2()
    my_function_3()
    my_function_4()
    my_function_5()

    # example with callable object
    class CallableClass:
        def __call__(self, *args, **kwargs):  # pylint: disable=W0621
            workload()

    callable_object = pyitt.task(CallableClass())
    callable_object()


def run_async_functions():
    # example for overlapped tasks
    @pyitt.task
    async def my_async_function_1():
        with pyitt.task():
            workload()
        await sleep(0.1)
        with pyitt.task():
            workload()

    @pyitt.task
    async def my_async_function_2():
        with pyitt.task():
            workload()
        await sleep(0.1)
        with pyitt.task():
            workload()

    @pyitt.task
    async def my_async_function_3():
        with pyitt.task():
            workload()
        await sleep(0.1)
        with pyitt.task():
            workload()

    class MyClass:
        @pyitt.task
        @classmethod
        async def my_method(cls):
            await my_async_function_3()

    async def main_async_function():
        task1 = create_task(my_async_function_1())
        task2 = create_task(my_async_function_2())
        task3 = create_task(MyClass.my_method())

        await task1
        await task2
        await task3

    run(main_async_function())


def run_generator_functions():
    @pyitt.task
    def xrange(val):
        yield from range(val)

    workload_task = pyitt.task('workload')
    for _ in xrange(2):
        with workload_task:
            workload()


def run_sample():
    run_sync_functions()
    run_async_functions()
    run_generator_functions()


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
