# Python Code Profiler

For measuring how much time different functions or pieces of code take to execute.

# Installing

## PyPi

`pip install codeprofile`

For more details, check the [Python Package Index project](https://pypi.org/project/code-profile/).

## Source Code

Hosted on [Github](https://github.com/mukatee/python-code-profile). At this time, practically just one file.

# Usage

Add the provided decorators to the pieces of code / functions you want to profile.

This document uses the term `trace point`.
It refers to part of code that is profiled as a single block.
If you profile execution time of a specific function, that function is the trace point.
If you profile a specific block of code inside a function, that block is the trace point.

## Functions

To trace / profile a function:

```python
from codeprofile import profiler
import time

@profiler.profile_func
def my_func():
    print("hello world")
    time.sleep(0.1)
    x = some_other_func()
    return int(x)
```

In the above, every time the function `my_func` is executed, its execution time is recorded.
It becomes a trace point named `my_func`.

## Code snippets

To trace the performance of a code snippet inside a function / module:

```python
from codeprofile import profiler

for x in range(100):
    with profiler.profile("block read"):
        block = read_block(x)
    with profiler.profile("db insert"):
        insert_into_database(block)
```

In the above, there are two trace points name `block read` and `db insert`.
The code above executes each trace point 100 times,
resulting in 100 performance measurements for each trace point.
The profiler will then provice access to cumulative, average, min, max, and count statistics
for each trace point.
If configured to keep the raw measurements, those and the median are also available per trace point.

Imagine the above `block read` as an example of reading a block of data over the network (e.g., scanning a blockchain).
And writing this to a database in `db insert`. Maybe it seems slow.
With the above profiling, you can look at your program and wonder, where does the time go?
Now there is a question we all would like to know..

## AsyncIO

[AsyncIO](https://docs.python.org/3/library/asyncio.html) is the Python way of making 
use of inherent processing delays in IO-intensive operations to execute code in parallel.
For example, the system might be waiting for some disk or network IO to proceed.
At such points, the CPU is just idle.
So AsyncIO is intended as a way to execute other code in parallel while waiting on IO.
Since Python has no true multithreading (the multi-processing module is not quite the same),
this can be a nice feature.

AsyncIO uses special keywords (such as `async`) and code-structures to manage all this.
Functions used with AsyncIO thus need to be defined with the `async` keyword.

Because of this, the approach to profile regular functions with `@profiler.profile_func`
does not work with AsyncIO, as the `profile_func` decorator is not `async`.
A different decorator using the `async` definition is provided for this purpose:

```python
from codeprofile import profiler
import asyncio

@profiler.profile_async_func
async def a_blocker(self):
    block = read_block() # <- assume this function uses asyncio to access network / disk
    await asyncio.sleep(1)
    insert_into_database(block) # <- again, assume this call uses asyncio access to a database

```

In the above example, `a_blocker` becomes a trace point measuring the function execution time for AsyncIO.

For code blocks inside AsyncIO methods / functions, the same approach as for other code blocks should work.

```python
from codeprofile import profiler

async def hundred_blocks():
    for x in range(100):
        with profiler.profile("block read"):
            block = read_block()
        with profiler.profile("db insert"):
            insert_into_database(block)
```

## Configuration

- `ignore_sleep`: If true, use a performance counter that ignores time spent in sleep mode. Defaults to false.
- `collect_raw`: If true, keep the raw measurement data for each `trace point`. Takes more memory, but gives access to more detailed profiling information. Defaults to true.

Setting them:

```python
from codeprofile import profiler

profiler.collect_raw = False #by default this is true
profiler.ignore_sleep = True #by default this is false
```

# Data Analysis

The performance data collected is stored and available as part of the `profiler` module.

## Access raw results

The following variables are available as part of the `profiler` module:

- `cumulative_times`: sum of all recorded execution times for a trace point.
- `max_times`: highest time per trace point
- `min_times`: minimum time per trace point
- `counts`: number of times a trace point execution has been recorded.
- `raw_times`: list of all recorded execution times per trace point.

The following function can be used if `collect_raw` is enabled:

- `median_times`: median time per trace point.

Like so:

```python
from codeprofile import profiler

cumulative_block_time = profiler.cumulative_times["block read"]
max_block_time = profiler.max_times["block read"]
min_block_time = profiler.min_times["block read"]
all_block_times = profiler.raw_times["block read"]

median_block_time = profiler.median("block read")
```

If you want to reset the statistics while running:

```python
from codeprofile import profiler

profiler.reset_stats()
```

## Summary Printouts

- `print_run_stats(*names, file=sys.stdout)`

The `names` parameter for `print_run_stats` is optional.
It defaults to all names.
A name is simply a reference to name of a trace point.

The `file` parameter allows writing the results to a file, a string, or elsewhere.
By default, it uses the system output, writing the summary to console.
You can also use an actual filesystem file as target, or build a string using `io.StringIO`,
or whatever else the Python filesystem can do.

## Export to CSV and Pandas

- `print_csv(*names, file=sys.stdout)`

The result of `print_csv` is a CSV file, where each column represents a trace-point.
The rows are not synchronized in any way, since only the person who implements the trace-points knows if they are related.
So each column is just a list of traced values (performance times) for that trace-point.
Each column has equal number of values, which is the largest number of points recorded for any trace-point.
The ones with fewer values have the last rows left empty (nan in Pandas).

```python
from codeprofile import profiler
import pandas as pd

with open("output.csv", "wb") as f:
    profiler.print_csv(file=f)

df = pd.read_csv("output.csv")
```

# Hierarchical profiling

You can also nest the trace profiling calls.
For example:

```python
from codeprofile import profiler

with profiler.profile("loop"):
    for x in range(100):
        with profiler.profile("block read"):
            block = read_block(x)
        with profiler.profile("db insert"):
            insert_into_database(block)
```

With the above, you would have the `loop` trace point collecting stats for the read and write operations together,
and the `block read` and `db insert` trace points for the specific operations.

# License

MIT


