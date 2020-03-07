__author__ = 'teemu kanstren'

import unittest
from codeprofile import profiler
import time
import io
import pandas as pd
import asyncio
import random

class StatsTests(unittest.TestCase):
    def assert_stats(self, txt, executions, cumulative, min, max, avg, median):
        self.assertTrue(f"n. executions:   {executions}" in txt)
        self.assertTrue(f"cumulative time: {cumulative}" in txt)
        self.assertTrue(f"min time:        {min}" in txt)
        self.assertTrue(f"max time:        {max}" in txt)
        self.assertTrue(f"avg. time:       {avg}" in txt)
        self.assertTrue(f"median time:     {median}" in txt)

    def assert_stats_list(self, txt, executions, cumulative_options, options):
        self.assertTrue(f"n. executions:   {executions}" in txt)
        found = False
        for option in cumulative_options:
            found = f"cumulative time: {option}" in txt or found
        self.assertTrue(found)
        found_min = False
        found_max = False
        found_avg = False
        found_median = False
        for option in options:
            found_min = f"min time:        {option}" in txt or found_min
            found_max = f"max time:        {option}" in txt or found_max
            found_avg = f"avg. time:       {option}" in txt or found_avg
            found_median = f"median time:     {option}" in txt or found_median
        self.assertTrue(found_min)
        self.assertTrue(found_max)
        self.assertTrue(found_avg)
        self.assertTrue(found_median)

    def setUp(self):
        profiler.reset_stats()

    def test_range(self):
        for x in range(20):
            with profiler.profile("sleep-one"):
                time.sleep(0.1)
            with profiler.profile("sleep-two"):
                time.sleep(0.2)

        f = io.StringIO()
        profiler.print_run_stats(file=f)
        stats_str = f.getvalue()
        splits = stats_str.split("sleep-two")
        self.assertEqual(2, len(splits), "Should have two profiled elements: sleep-one and sleep-two")
        sleep_one = splits[0]
        self.assert_stats(sleep_one, 20, 2.0, 0.10, 0.10, 0.10, 0.10)

        sleep_two = splits[1]
        self.assert_stats(sleep_two, 20, 4.0, 0.20, 0.20, 0.20, 0.20)

        f = io.StringIO()
        profiler.print_csv(file=f)
        stats_str = f.getvalue()
        split = stats_str.split("\n")
        self.assertEqual(22, len(split))

        df = pd.read_csv(io.StringIO(stats_str))
        print(df.describe())
        df_s1 = df["sleep-one"]
        nans = df_s1.isna().sum()
        self.assertEqual(0, nans)
        mean = df_s1.mean()
        self.assertAlmostEqual(mean, 0.1, delta=0.05)

        cols = df.columns
        df_s2 = df["sleep-two"]
        nans = df_s2.isna().sum()
        self.assertEqual(0, nans)
        mean = df_s2.mean()
        self.assertAlmostEqual(mean, 0.2, delta=0.05)

    def test_different_ranges(self):
        for x in range(20):
            with profiler.profile("sleep-one"):
                time.sleep(0.1)

        for x in range(10):
            with profiler.profile("sleep-two"):
                time.sleep(0.2)

        f = io.StringIO()
        profiler.print_run_stats(file=f)
        stats_str = f.getvalue()
        splits = stats_str.split("sleep-two")
        self.assertEqual(2, len(splits), "Should have two profiled elements: sleep-one and sleep-two")
        sleep_one = splits[0]
        self.assert_stats(sleep_one, 20, 2.0, 0.10, 0.10, 0.10, 0.10)

        sleep_two = splits[1]
        self.assert_stats(sleep_two, 10, 2.0, 0.20, 0.20, 0.20, 0.20)

        f = io.StringIO()
        profiler.print_csv(file=f)
        stats_str = f.getvalue()
        split = stats_str.split("\n")
        self.assertEqual(22, len(split))

        df = pd.read_csv(io.StringIO(stats_str))
        print(df.describe())
        df_s1 = df["sleep-one"]
        nans = df_s1.isna().sum()
        self.assertEqual(0, nans)
        mean = df_s1.mean()
        self.assertAlmostEqual(mean, 0.1, delta=0.05)

        cols = df.columns
        df_s2 = df["sleep-two"]
        nans = df_s2.isna().sum()
        self.assertEqual(10, nans)
        mean = df_s2.mean()
        self.assertAlmostEqual(mean, 0.2, delta=0.05)

    def test_trace_hierachy(self):
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
        self.assert_stats(in1, 5, 0.5, 0.1, 0.1, 0.1, 0.1)

        in2 = splits[2]
        self.assert_stats(in2, 5, 0.76, 0.15, 0.15, 0.15, 0.15)

        top = splits[3]
        self.assert_stats_list(top, 1, [1.28, 1.27], [1.28, 1.27])


    def test_method_trace(self):
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
        print(stats_str)

        binder = splits[1]
        self.assert_stats_list(binder, 1, [0.78], [0.78])

        inner1 = splits[2]
        self.assert_stats(inner1, 5, 0.5, 0.1, 0.1, 0.1, 0.1)

        inner2 = splits[3]
        self.assert_stats_list(inner2, 5, [0.26, 0.27],[0.05])

    @profiler.profile_async_func
    async def a_sleeper_2(self):
        await asyncio.sleep(random.randint(1,4))

    async def a_sleeper(self):
        with profiler.profile("async-inner"):
            await asyncio.sleep(random.randint(1,4))

    async def run_async(self):
        with profiler.profile("async-top"):
            coroutines = []
            for x in range(500):
                coroutines.append(self.a_sleeper())
            await asyncio.gather(*coroutines)

    async def run_async_func(self):
        with profiler.profile("async-top"):
            coroutines = []
            for x in range(500):
                coroutines.append(self.a_sleeper_2())
            await asyncio.gather(*coroutines)

    def test_asyncio_trace(self):
        asyncio.run(self.run_async())
        profiler.print_run_stats()

    def test_asyncio_trace_func(self):
        asyncio.run(self.run_async_func())
        profiler.print_run_stats()
