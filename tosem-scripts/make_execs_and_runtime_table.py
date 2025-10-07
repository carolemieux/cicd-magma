import os
from math import isnan
from statistics import median
import sys
import pandas as pd
import matplotlib.pyplot as plt
import json
import numpy as np
from scipy.stats import mannwhitneyu

BASE_DATA_DIR= "../tosem-results/aux-data-results"

fuzzers = ['afl', 'aflplusplus', 'aflgo', 'aflgoexp', 'ffd','windranger', 'tunefuzz']

def round_to_millions_or_thousands(number, bold_units=False):
    """
    Given a number, render as number of thousands+"k" or
    millions + "M"
    e.g.
    :param number: a number
    :param bold_units: whether to use bold units
    :return:
    >>> round_to_millions_or_thousands(1234)
    '1k'
    >>> round_to_millions_or_thousands(17123)
    '17k'
    >>> round_to_millions_or_thousands(17123.142)
    '17k'
    >>> round_to_millions_or_thousands(1713)
    '2k'
    >>> round_to_millions_or_thousands(713)
    '0.7k'
    >>> round_to_millions_or_thousands(412)
    '0.4k'
    >>> round_to_millions_or_thousands(41201012)
    '41M'
    >>> round_to_millions_or_thousands(1750840)
    '2M'
    >>> round_to_millions_or_thousands(175084)
    '0.2M'
    >>> round_to_millions_or_thousands(625084)
    '0.6M'
    >>> round_to_millions_or_thousands(955084)
    '1M'
    >>> round_to_millions_or_thousands(94003)
    '94k'
    >>> round_to_millions_or_thousands(99003)
    '99k'
    >>> round_to_millions_or_thousands(99500)
    '0.1M'
    """
    if number < 1000:
        k = "\\textbf{k}" if bold_units else "k"
        ks = round(number / 1000, 1)
        return f"{ks}{k}"
    elif number < 99500:
        k = "\\textbf{k}" if bold_units else "k"
        ks = round(number / 1000, 0)
        ks = int(ks)
        return f"{ks}{k}"
    elif number < 950000:
        M = "\\textbf{M}" if bold_units else "M"
        Ms = round(number / 1000_000, 1)
        return f"{Ms}{M}"
    else:
        M = "\\textbf{M}" if bold_units else "M"
        Ms = round(number / 1000_000, 0)
        Ms = int(Ms)
        return f"{Ms}{M}"

def get_driver_to_seed_num_dict():
    """
    Get the number of starting seeds for each driver
    :return: a dictionary of driver name to number of seeds
    """
    seeds_file = os.path.join(BASE_DATA_DIR, "num_seeds.csv")
    out_dict = {}
    with open(seeds_file) as f:
        for line in f:
            if line.startswith("#"):
                continue
            else:
                driver, num_seeds = line.strip().split(",")
                num_seeds = int(num_seeds)
                out_dict[driver] = num_seeds
    return out_dict

def get_technique_full_info(fuzzer):
    """
    Gets the full execs_done, fuzz_time info for the fuzzer
    :param fuzzer: fuzzer to fetch info for
    :return: a dictionary of fuzzer name to benchmark name to (driver, list of execs done, list of fuzz times)
    """
    postfix= "_execs_and_fuzz_time.csv"
    fuzzer_path = os.path.join(BASE_DATA_DIR, f"{fuzzer}{postfix}")
    inner_out_dict = {}
    with open(fuzzer_path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            else:
                fuzzer,benchmark,driver,run,execs_done,fuzz_time = line.strip().split(",")
                if benchmark not in inner_out_dict:
                    inner_out_dict[benchmark] = (driver, [execs_done], [fuzz_time])
                else:
                    inner_out_dict[benchmark][1].append(execs_done)
                    inner_out_dict[benchmark][2].append(fuzz_time)
    out_dict = {fuzzer:inner_out_dict}
    return out_dict

def retrieve_lowest_or_highest_for_each_benchmark(fuzzers, data_type: str, lowest_or_highest: str):
    """
    Returns a dictionary mapping benchmark to the fuzzer that is relatively lower/higher
    in metric value than everyone else.
    :param fuzzers:
    :param data_type:
    :return:
    """
    if data_type == "execs":
        idx = 1
    elif data_type == "fuzz_time":
        idx = 2
    else:
        print("Unknown data type to get p-values for:", data_type, file=sys.stderr)
        exit(1)
    if lowest_or_highest == "lowest":
        alternative = 'less'
    elif lowest_or_highest == "highest":
        alternative = 'greater'
    else:
        print("Unknown direction to test: ", lowest_or_highest, file=sys.stderr)
        exit(1)

    data = {}
    for fuzzer in fuzzers:
        data.update(get_technique_full_info(fuzzer))
    first_fuzzer = fuzzers[0]
    benchmarks = sorted(data[first_fuzzer].keys())
    out_dict = {}
    for benchmark in benchmarks:
        if "php" in benchmark:
            total_execs = {fuzzer: [float(n) for n in data[fuzzer][benchmark][idx]] for fuzzer in fuzzers if fuzzer !="windranger"}
        else:
            total_execs = {fuzzer: [float(n) for n in data[fuzzer][benchmark][idx]] for fuzzer in fuzzers}
        max_worst_than = 0
        max_worst_fuzzer = None
        for fuzzer in total_execs:
            p_values = [mannwhitneyu(total_execs[fuzzer], total_execs[other], alternative='less').pvalue for other in total_execs.keys() if other != fuzzer]
            num_siggy_worse = len([val for val in p_values if val < 0.05])
            if num_siggy_worse > max_worst_than:
                max_worst_fuzzer = fuzzer
                max_worst_than = num_siggy_worse
        if max_worst_fuzzer is not None and max_worst_than >= 3:
            out_dict[benchmark] = max_worst_fuzzer
    return out_dict

def write_table_with_fuzzers(fuzzers=fuzzers, print_seeds = False):
    """
    Writes a LaTeX table where:
    - first column is the driver name
    - second column is the number of seeds, in k (if print_seeds)
    - next len(fuzzers) columns are the median execs for each fuzzer
    - next len(fuzzers) columns are the median real fuzz time for each fuzzer
    :param fuzzers: list of fuzzers to consider
    :param print_seeds: whether or not to print
    :return: none, prints to studout
    """
    if len(fuzzers) == 0:
        print("nothing to see here")
    highlight_text = "\\underline"
    num_seeds_per_driver = get_driver_to_seed_num_dict()
    data = {}
    for fuzzer in fuzzers:
        data.update(get_technique_full_info(fuzzer))
    first_fuzzer = fuzzers[0]
    benchmarks = sorted(data[first_fuzzer].keys())


    to_highlight_execs = retrieve_lowest_or_highest_for_each_benchmark(fuzzers, "execs", "lowest")
    how_many_highlights_per_fuzzer = {fuzzer: len([v for v in to_highlight_execs.values() if v == fuzzer]) for fuzzer in fuzzers}
    print(f"Number of times highlighted for execs: {how_many_highlights_per_fuzzer}", file=sys.stderr)

    to_highlight_fuzz_times = retrieve_lowest_or_highest_for_each_benchmark(fuzzers, "fuzz_time", "lowest")

    how_many_highlights_per_fuzzer = {fuzzer: len([v for v in to_highlight_fuzz_times.values() if v == fuzzer]) for fuzzer in fuzzers}
    print(f"Number of times highlighted for fuzz times: {how_many_highlights_per_fuzzer}", file=sys.stderr)

    for benchmark in benchmarks:
        # Print the first two columns first
        out_str = benchmark.replace("_", "\\_")
        if print_seeds:
            driver = data[first_fuzzer][benchmark][0]
            if driver in num_seeds_per_driver:
                seeds = num_seeds_per_driver[driver]
            elif f"{driver}_mini" in num_seeds_per_driver:
                seeds = num_seeds_per_driver[f"{driver}_mini"]
            else:
                print("Cannot find number of seeds for driver " + driver, file=sys.stderr)
                exit(1)
            out_str += f" & {round_to_millions_or_thousands(int(seeds))}"
        # Now print all the median execs columns
        fuzzer_to_highlight = to_highlight_execs.get(benchmark, "")
        for fuzzer in fuzzers:
            # PHP is missing ofr windranger
            if benchmark not in data[fuzzer]:
                out_str += f"& $\\times$ "
                continue
            all_execs_for_fuzzer_and_bench = data[fuzzer][benchmark][1]
            execs_as_floats = [float(e) for e in all_execs_for_fuzzer_and_bench]
            if any([isnan(e) for e in execs_as_floats]):
                execs_as_floats = [e for e in execs_as_floats if not isnan(e)]
                print(f"For {fuzzer}, {benchmark}, we have some NaN execs. Averaging over {len(execs_as_floats)} values",file=sys.stderr)
            if len(execs_as_floats) == 0:
                print(f"For {fuzzer}, {benchmark}, we have no execs", file=sys.stderr)
                median_execs= ""
            else:
                median_execs = median(execs_as_floats)
            rendered_execs = round_to_millions_or_thousands(median_execs)
            if fuzzer == fuzzer_to_highlight:
                out_str += "& "+ highlight_text +"{" + rendered_execs +"}"
            else:
                out_str += f"& {rendered_execs} "
        # gap for formatting
        out_str += " & "
        # and the true fuzz_time columns
        fuzzer_to_highlight = to_highlight_fuzz_times.get(benchmark, "")
        for fuzzer in fuzzers:
            if benchmark not in data[fuzzer]:
                out_str += f"& $\\times$ "
                continue
            all_fuzz_times_for_fuzzer_and_bench = data[fuzzer][benchmark][2]
            fuzztimes_as_floats = [float(e) for e in all_fuzz_times_for_fuzzer_and_bench]
            if any([isnan(e) for e in fuzztimes_as_floats]):
                fuzztimes_as_floats = [e for e in fuzztimes_as_floats if not isnan(e)]
                print(f"For {fuzzer}, {benchmark}, we have some NaN fuzztimes. Averaging over {len(fuzztimes_as_floats)} values",file=sys.stderr)
            if len(execs_as_floats) == 0:
                print(f"For {fuzzer}, {benchmark}, we have no fuzz_times", file=sys.stderr)
                rendered_fuzz_times= ""
            else:
                median_fuzz_times = median(fuzztimes_as_floats)
                rendered_fuzz_times = int(median_fuzz_times)
            if fuzzer == fuzzer_to_highlight:
                out_str += "& "+ highlight_text +"{" + str(rendered_fuzz_times) +"}"
            else:
                out_str += f"& {rendered_fuzz_times} "
        out_str += "\\\\"
        print(out_str)

if __name__ == "__main__":
    write_table_with_fuzzers(fuzzers)