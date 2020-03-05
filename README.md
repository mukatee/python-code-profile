# Python Code Profile

For measuring how much time different functions or pieces of code take to execute.

# Installing

## PyPi

With pip:
`pip install code-profile`

For more details, check the [Python Package Index project](https://pypi.org/project/code-profile/).

## Code

Or go to [Github](https://github.com/mukatee/python-code-profile) and play with it yourself.

# Usage

This project provides decorators that just time the code / functions you set them to.
The performance data collected is available in

- print_run_stats(*names, file=sys.stdout)
- print_csv(*names, file=sys.stdout)

The *names* parameter in the above is an optional argument.
You can omit it (None value) to default to all names.
A name is simply a reference to name of a monitoring point.
If you use one of the annotations to trace the performance of a method,
the name of that method is used as a name for the monitoring point.

The *file* parameter is simply there to allow using specific file to write the results to.

- cumulative_times: sum of time how long each trace point has been executing. if the point is executed 10 times, this is sum of time taken for all those 10 times.
- max_times: highest time per trace point
- min_times: minimum time per trace point
- median_times: median time per trace point. requires storing raw data.

These are all provided on summary report than can be accessed with the print_run_stats(), or the print_csv().
Or you can access them from the profiler variables / methods.

General configuration options:

- ignore_sleep: If true, use a performance counter that ignores time spent in sleep mode. Defaults to false.
- collect_raw: If true, keep the raw measurement data for each point execution. Takes more memory, but gives options to dump the csv using print_csv() for further analysis. Defaults to true.

## Functions

To trace the performance of a function:

## Code snippets

To trace the performance of a code snippet:

## AsyncIO

To trace an AsyncIO based code block, just use the same approach as for a regular code block.
To trace an AsyncIO based function, use the specific profile_async_func() method.

# Data Analysis

## Access raw results

## Summary Printouts

## Export to CSV and Pandas

# Configuration


