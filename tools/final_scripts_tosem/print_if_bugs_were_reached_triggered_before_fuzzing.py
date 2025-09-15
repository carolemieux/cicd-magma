#!/bin/bash

from make_execs_and_runtime_table import get_technique_full_info, fuzzers
from process_bug_analysis import get_result_arrays

timeout = 600
poll = 5

def happened_before_fuzzing_started(bug_time, pure_fuzz_time):
    """
    Did this bug triggering/reaching time happen before fuzzing started?
    Essentially, the first (timeout -pure_fuzz_time) seconds are spent
    loading the queue. We know that bug_time is between (bug_time - POLL, bug_time]
    If that interval is wholly in loading the queue, say 'yes'
    If that interval is wholly while fuzzing, say 'no'
    Else, say 'maybe', and the time before the bug would have had to happen
    for it to be 'yes'
    ASSUME: off-by-poll error has been fixed
    :param bug_time: time bug was reached/triggered
    :param pure_fuzz_time: time spend fuzzing
    :return:
    >>> happened_before_fuzzing_started(5, 600)
    'maybe (600s of fuzzing)'
    >>> happened_before_fuzzing_started(5, 599)
    'maybe (if happened in 1s rather than 5s)'
    >>> happened_before_fuzzing_started(5, 596)
    'maybe (if happened in 4s rather than 5s)'
    >>> happened_before_fuzzing_started(5, 590)
    'yes'
    >>> happened_before_fuzzing_started(10, 596)
    'no'
    >>> happened_before_fuzzing_started(25, 590)
    'no'
    >>> happened_before_fuzzing_started(25, 298)
    'yes'
    >>> happened_before_fuzzing_started(25, 578)
    'maybe (if happened in 22s rather than 25s)'
    """
    when_finished_queue = timeout - pure_fuzz_time
    if bug_time < when_finished_queue:
        return 'yes'
    elif bug_time - poll < when_finished_queue:
        return f'maybe (if happened in {when_finished_queue}s rather than {bug_time}s)'
    elif when_finished_queue == 0 and bug_time < poll + 1:
        return f'maybe ({timeout}s of fuzzing)'
    else:
        return 'no'

# get mappings from fuzzer -> benchmark -> [raw times reached/triggered]
# False: without instrumentation
total_reached, total_triggered = get_result_arrays(False, sensitivity=False)

# Get mapping from fuzzer -> benchmark -> (num seeds, [execs], [true fuzzing time])
data = {}
for fuzzer in fuzzers:
    data.update(get_technique_full_info(fuzzer))

for fuzzer in fuzzers:
    for benchmark in total_reached[fuzzer]:
        true_fuzzing_times = data[fuzzer][benchmark][2]
        reached_times = total_reached[fuzzer][benchmark]
        if 0 < len(reached_times) < 10:
            print("!!printing out the deets: {fuzzer}, {benchmark}")
            print("!!",reached_times)
            print("!!",true_fuzzing_times)
        for i, reached_time in enumerate(reached_times):
            true_fuzzing_time = true_fuzzing_times[i]
            if true_fuzzing_time == 'NaN':
                print(f'reached,{fuzzer},{benchmark},{i},NaN')
                continue
            # TODO: do we subtract 5 here or earlier??
            res = happened_before_fuzzing_started(int(reached_time) - 5 , int(true_fuzzing_time))
            print(f'reached,{fuzzer},{benchmark},{i},{res}')
    for benchmark in total_triggered[fuzzer]:
        true_fuzzing_times = data[fuzzer][benchmark][2]
        triggered_times = total_triggered[fuzzer][benchmark]
        if 0 < len(triggered_times) < 10:
            print("!!printing out the deets: {fuzzer}, {benchmark}")
            print("!!",triggered_times)
            print("!!",true_fuzzing_times)
        for i, triggered_time in enumerate(triggered_times):
            true_fuzzing_time = true_fuzzing_times[i]
            if true_fuzzing_time == 'NaN':
                print(f'triggered,{fuzzer},{benchmark},{i},NaN')
                continue
            # TODO: do we subtract 5 here or earlier??
            res = happened_before_fuzzing_started(int(triggered_time) - 5 , int(true_fuzzing_time))
            print(f'triggered,{fuzzer},{benchmark},{i},{res}')
        #triggered_times = total_triggered[fuzzer][benchmark]

# special handling for libfuzzer. because of fork=1 setting, there
# is not a defined queue-traversal time. We assume fuzzing starts for real 2s
# in, as this is the first time listed in nearly all libfuzzer logs (some
# logs list 1 or 3 seconds, but this won't affect our analysis due to the
# 5-second poll time)
fuzzer = "libfuzzer"
for benchmark in total_reached[fuzzer]:
    reached_times = total_reached[fuzzer][benchmark]
    true_fuzzing_time = 598
    if 0 < len(reached_times) < 10:
        print("!!printing out the deets: {fuzzer}, {benchmark}")
        print("!!", reached_times)
    for i, reached_time in enumerate(reached_times):
        res = happened_before_fuzzing_started(int(reached_time)- 5, true_fuzzing_time)
        print(f'reached,{fuzzer},{benchmark},{i},{res}')
for benchmark in total_triggered[fuzzer]:
    triggered_times = total_triggered[fuzzer][benchmark]
    true_fuzzing_time = 598
    if 0 < len(triggered_times) < 10:
        print("!!printing out the deets: {fuzzer}, {benchmark}")
        print("!!", triggered_times)
    for i, triggered_time in enumerate(triggered_times):
        res = happened_before_fuzzing_started(int(triggered_time)- 5, true_fuzzing_time)
        print(f'triggered,{fuzzer},{benchmark},{i},{res}')