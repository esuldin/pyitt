#!/usr/bin/env python
import pyitt

# pylint: disable=C0411
from argparse import ArgumentParser
from vtune_tool import run_vtune_hotspot_collection
from asyncio import create_task, run, sleep


async def run_inc_counter():
    counter = pyitt.Counter('inc counter')
    await sleep(0.1)

    counter.inc()
    await sleep(0.1)

    counter.inc(10)
    await sleep(0.1)

    counter += 20
    await sleep(0.1)

    counter.set(40)
    await sleep(0.1)


async def run_dec_counter():
    counter = pyitt.Counter('dec counter', 'my domain', 40)
    await sleep(0.1)

    counter.dec()
    await sleep(0.1)

    counter.dec(10)
    await sleep(0.1)

    counter -= 20
    await sleep(0.1)

    counter.set(1)
    await sleep(0.1)


async def run_sample():
    task1 = create_task(run_inc_counter())
    task2 = create_task(run_dec_counter())

    await task1
    await task2


if __name__ == '__main__':
    parser = ArgumentParser(description='The sample that demonstrates the use of wrappers for the Counter API.')
    parser.add_argument('--run-sample',
                        help='Runs code that uses wrappers for the Counter API.',
                        action='store_true')
    args = parser.parse_args()

    if args.run_sample:
        run(run_sample())
    else:
        run_vtune_hotspot_collection(['python', __file__, '--run-sample'])
