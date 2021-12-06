__author__ = 'teemu kanstren'

import pytest
from codeprofile import profiler
import time
import io
import pandas as pd
import asyncio
import random

def assert_stats(txt, executions, cumulative, min, max, avg, median):
    assert f"n. executions:   {executions}" in txt
    assert f"cumulative time: {cumulative}" in txt
    assert f"min time:        {min}" in txt
    assert f"max time:        {max}" in txt
    assert f"avg. time:       {avg}" in txt
    assert f"median time:     {median}" in txt

def assert_stats_list(txt, executions, cumulative_options, options):
    assert f"n. executions:   {executions}" in txt
    found = False
    for option in cumulative_options:
        found = f"cumulative time: {option}" in txt or found
    assert found
    found_min = False
    found_max = False
    found_avg = False
    found_median = False
    for option in options:
        found_min = f"min time:        {option}" in txt or found_min
        found_max = f"max time:        {option}" in txt or found_max
        found_avg = f"avg. time:       {option}" in txt or found_avg
        found_median = f"median time:     {option}" in txt or found_median
    assert found_min
    assert found_max
    assert found_avg
    assert found_median

@pytest.fixture(scope="function")
def new_profiler():
    profiler.reset_stats()

def test_range(new_profiler):
    for x in range(20):
        with profiler.profile("sleep-one"):
            time.sleep(0.1)
        with profiler.profile("sleep-two"):
            time.sleep(0.2)

    f = io.StringIO()
    profiler.print_run_stats(file=f)
    stats_str = f.getvalue()
    splits = stats_str.split("sleep-two")
    assert len(splits) == 2, "Should have two profiled elements: sleep-one and sleep-two"
    sleep_one = splits[0]
    assert_stats(sleep_one, 20, 2.0, 0.10, 0.10, 0.10, 0.10)

    sleep_two = splits[1]
    assert_stats(sleep_two, 20, 4.0, 0.20, 0.20, 0.20, 0.20)

    f = io.StringIO()
    profiler.print_csv(file=f)
    stats_str = f.getvalue()
    split = stats_str.split("\n")
    assert len(split) == 22

    df = pd.read_csv(io.StringIO(stats_str))
    print(df.describe())
    df_s1 = df["sleep-one"]
    nans = df_s1.isna().sum()
    assert nans == 0
    mean = df_s1.mean()
    #https://stackoverflow.com/questions/8560131/pytest-assert-almost-equal
    assert mean == pytest.approx(0.1, 0.05)

    df_s2 = df["sleep-two"]
    nans = df_s2.isna().sum()
    assert nans == 0
    mean = df_s2.mean()
    assert mean == pytest.approx(0.2, 0.05)

def test_different_ranges(new_profiler):
    for x in range(20):
        with profiler.profile("sleep-one"):
            time.sleep(0.1)

    for x in range(10):
        with profiler.profile("sleep-two"):
            sleeptime = 0.1*(1+x%2)
            time.sleep(sleeptime)

    f = io.StringIO()
    profiler.print_run_stats(file=f)
    stats_str = f.getvalue()
    splits = stats_str.split("sleep-two")
    assert len(splits) == 2, "Should have two profiled elements: sleep-one and sleep-two"
    sleep_one = splits[0]
    assert_stats(sleep_one, 20, 2.0, 0.10, 0.10, 0.10, 0.10)

    sleep_two = splits[1]
    assert_stats(sleep_two, 10, 1.50, 0.10, 0.20, 0.15, 0.15)

    f = io.StringIO()
    profiler.print_csv(file=f)
    stats_str = f.getvalue()
    split = stats_str.split("\n")
    assert len(split) == 22

    df = pd.read_csv(io.StringIO(stats_str))
    print(df.describe())
    df_s1 = df["sleep-one"]
    nans = df_s1.isna().sum()
    assert nans == 0
    mean = df_s1.mean()
    assert mean == pytest.approx(0.1, 0.05)

    df_s2 = df["sleep-two"]
    nans = df_s2.isna().sum()
    assert nans == 10
    mean = df_s2.mean()
    print(mean)
    assert mean == pytest.approx(0.15, 0.05)

def test_trace_hierachy(new_profiler):
    with profiler.profile("top"):
        for x in range(5):
            with profiler.profile("in1"):
                time.sleep(0.1)
            with profiler.profile(("in2")):
                time.sleep(0.15)
    f = io.StringIO()
    profiler.print_run_stats(file=f)
    stats_str = f.getvalue()
    splits = stats_str.split(":\n")

    in1 = splits[1]
    assert_stats(in1, 5, 0.5, 0.1, 0.1, 0.1, 0.1)

    in2 = splits[2]
    assert_stats(in2, 5, 0.75, 0.15, 0.15, 0.15, 0.15)

    top = splits[3]
    assert_stats_list(top, 1, [1.25, 1.26], [1.25, 1.26])

def test_method_trace(new_profiler):
    @profiler.profile_func
    def inner1():
        time.sleep(0.1)
    @profiler.profile_func
    def inner2():
        time.sleep(0.05)
    with profiler.profile("binder"):
        for x in range(5):
            inner1()
            inner2()

    f = io.StringIO()
    profiler.print_run_stats(file=f)

    stats_str = f.getvalue()
    splits = stats_str.split(":\n")
    binder = splits[1]
    assert_stats_list(binder, 1, [0.75, 0.76,], [0.75, 0.76,])

    inner1 = splits[2]
    assert_stats(inner1, 5, 0.5, 0.1, 0.1, 0.1, 0.1)

    inner2 = splits[3]
    assert_stats_list(inner2, 5, [0.25, 0.26, 0.27],[0.05])

def test_throw_error(new_profiler):
    for x in range(20):
        with profiler.profile("sleep-one"):
            time.sleep(0.1)
        try:
            with profiler.profile("throw error"):
                time.sleep(0.1)
                if (x > 1):
                    raise Exception("oops")
        except:
            pass

    f = io.StringIO()
    profiler.print_run_stats(file=f)
    stats_str = f.getvalue()
    splits = stats_str.split(":\n")

    in1 = splits[1]
    assert_stats(in1, 20, 2.0, 0.1, 0.1, 0.1, 0.1)

    in2 = splits[2]
    assert_stats(in2, 2, 0.2, 0.1, 0.1, 0.1, 0.1)

def test_count_zero(new_profiler):
    for x in range(2):
        with profiler.profile("sleep-one"):
            time.sleep(0.1)
    profiler.counts["zero_count"] = 0
    profiler.cumulative_times["zero_count"] = 0

    f = io.StringIO()
    profiler.print_run_stats(file=f)
    stats_str = f.getvalue()
    splits = stats_str.split(":\n")

    in1 = splits[1]
    assert_stats(in1, 2, 0.2, 0.1, 0.1, 0.1, 0.1)

    in2 = splits[2]
    assert_stats(in2, 0, 0, 0, 0, "NA", "NA")

@profiler.profile_async_func
async def a_sleeper_2():
    await asyncio.sleep(random.randint(1,4))

async def a_sleeper():
    with profiler.profile("async-inner"):
        await asyncio.sleep(random.randint(1,4))

async def run_async():
    with profiler.profile("async-top"):
        coroutines = []
        for x in range(500):
            coroutines.append(a_sleeper())
        await asyncio.gather(*coroutines)

async def run_async_func():
    with profiler.profile("async-top"):
        coroutines = []
        for x in range(500):
            coroutines.append(a_sleeper_2())
        await asyncio.gather(*coroutines)

def test_asyncio_trace(new_profiler):
    asyncio.run(run_async())
    profiler.print_run_stats()

def test_asyncio_trace_func(new_profiler):
    asyncio.run(run_async_func())
    profiler.print_run_stats()

