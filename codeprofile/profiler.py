__author__ = 'teemu kanstren'

from contextlib import contextmanager
from typing import Dict, List

from collections import defaultdict
import sys
import statistics
import time
import functools

import codeprofile

#TODO: metrics for last N observations
cumulative_times:Dict[str, float] = defaultdict(int)
max_times:Dict[str, float] = defaultdict(lambda:-sys.maxsize)
min_times:Dict[str, float] = defaultdict(lambda:sys.maxsize)
counts:Dict[str, int] = defaultdict(int)
raw_times:Dict[str, List] = defaultdict(list)
ignore_sleep:bool = False
collect_raw = True

def calculate_median(name):
    return statistics.median(raw_times[name])

def reset_stats():
    cumulative_times.clear()
    max_times.clear()
    min_times.clear()
    counts.clear()
    raw_times.clear()

def print_help():
    print(f"Codeprofile v.{codeprofile.__version__}")
    print()
    print("For profiling some parts/functions of your Python code.")
    print("Use as an imported module in your code. See README.md for more info.")

if __name__ == "__main__":
    print_help()

def profile_async_func(func):
    #https://stackoverflow.com/questions/42043226/using-a-coroutine-as-decorator/
    @functools.wraps(func)
    async def wrapped(*args):
         # Some fancy foo stuff
        return await func(*args)
    return wrapped

def profile_func(func):
    @functools.wraps(func)
    def newfunc(*args, **kwargs):
        if ignore_sleep:
            startTime = time.process_time()
        else:
            startTime = time.perf_counter()
        result = func(*args, **kwargs)
        if ignore_sleep:
            elapsedTime = time.process_time() - startTime
        else:
            elapsedTime = time.perf_counter() - startTime
        name = func.__name__
        cumulative_times[name] += elapsedTime
        if elapsedTime > max_times[name]: max_times[name] = elapsedTime
        if elapsedTime < min_times[name]: min_times[name] = elapsedTime
        counts[name] += 1
        if collect_raw:
            raw_times[name].append(elapsedTime)
        return result
    return newfunc

@contextmanager
def profile(name):
    #Timing options: https://stackoverflow.com/questions/85451/pythons-time-clock-vs-time-time-accuracy
    if ignore_sleep:
        startTime = time.process_time()
    else:
        startTime = time.perf_counter()
    yield
    if ignore_sleep:
        elapsedTime = time.process_time() - startTime
    else:
        elapsedTime = time.perf_counter() - startTime
    cumulative_times[name] += elapsedTime
    if elapsedTime > max_times[name]: max_times[name] = elapsedTime
    if elapsedTime < min_times[name]: min_times[name] = elapsedTime
    counts[name] += 1
    if collect_raw:
        raw_times[name].append(elapsedTime)

def print_run_stats(*names, file=sys.stdout):
    if len(names) == 0:
        names = cumulative_times.keys()
        names = sorted(names)
    for name in names:
        cumulative_time = cumulative_times[name]
        max_time = max_times[name]
        min_time = min_times[name]
        count = counts[name]
        if count > 0:
            avg = float(cumulative_time)/float(count)
        else:
            max_time = 0
            min_time = 0
            avg = "NA"
        #if needed, could also do running median: https://stackoverflow.com/questions/10657503/find-running-median-from-a-stream-of-integers
        if collect_raw and count > 0:
            median = statistics.median(raw_times[name])
        else:
            median = "NA" #its not available
        print(f"{name}:\n"
              f"    n. executions:   {count},\n"
              f"    cumulative time: {cumulative_time},\n"
              f"    min time:        {min_time},\n"
              f"    max time:        {max_time},\n"
              f"    avg. time:       {avg},\n"
              f"    median time:     {median}\n",
              file=file)

def print_csv(*names, file=sys.stdout):
    if not collect_raw:
        print("collecting raw times is disabled. not writing per execution point csv files.")
        print("also skipping median from summary for the same reason.")
    if len(names) == 0:
        names = cumulative_times.keys()
        names = sorted(names)
    csv = "name, cumulative time, avg time, max time, min time, run count, median time\n"
    for name in names:
        cumulative_time = cumulative_times[name]
        max_time = max_times[name]
        min_time = min_times[name]
        count = counts[name]
        avg = float(cumulative_time)/float(count)
        #if needed, could also do running median: https://stackoverflow.com/questions/10657503/find-running-median-from-a-stream-of-integers
        if collect_raw:
            median = calculate_median(name)
        else:
            median = "NA" #its not available
        csv += f"{name}, {avg}, {max_time}, {min_time}, {count}, {median}\n"

    max_len = 0
    for key in raw_times:
        cur_len = len(raw_times[key])
        if cur_len > max_len:
            max_len = cur_len

    if collect_raw:
        #the header
        keys = raw_times.keys()
        #rather join with "," than ", " as pandas dataframes take whitespace as part of column name etc.
        header = ",".join(keys)
        rows = [header]
        for x in range(max_len):
            #https://waymoot.org/home/python_string/
            #https://stackoverflow.com/questions/2414667/python-string-class-like-stringbuilder-in-c
            row = [str(raw_times[name][x])
                   if len(raw_times[name]) > x
                   else ''
                   for name in keys]
            row_str = ','.join(row)
            rows.append(row_str)
        csv = "\n".join(rows)
    print(csv, file=file)
