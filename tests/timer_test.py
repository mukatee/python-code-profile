__author__ = 'teemu kanstren'

import time
import codeprofile.profiler as profiler

def foo():
    time.sleep(0.1)

@profiler.profile_func
def bar():
    time.sleep(0.2)

bar()
profiler.print_run_stats()

for x in range(20):
    with profiler.profile("foo-perf"):
        foo()
    with profiler.profile("bar-perf"):
        bar()

#print(times)

profiler.print_run_stats()
profiler.print_csv()
