import os
from scipy.stats import mannwhitneyu
from statistics import median
import sys

BASE_RESULTS_DIR= '../tosem-results/aux-data-results'


def retrieve_lowest_or_highest_for_each_benchmark(data, lowest_or_highest: str, target_coverage):
    """
    Returns a dictionary mapping benchmark to the fuzzer that is relatively lower/higher
    in metric value than everyone else.
    :param dictionary from fuzzer name to benchmark name to data
    :param lowest_or_highest: 'lowest' or 'highest'
    :return:
    """
    if lowest_or_highest == "lowest":
        alternative = 'less'
    elif lowest_or_highest == "highest":
        alternative = 'greater'
    else:
        print("Unknown direction to test: ", lowest_or_highest, file=sys.stderr)
        exit(1)

    fuzzers = list(data.keys())
    benchmarks = set()
    for fuzzer_name in fuzzers:
        benchmarks.update(data[fuzzer_name].keys())

    out_dict = {}
    for benchmark in sorted(benchmarks):
        if target_coverage and benchmark == 'openssl_20_3' or benchmark == 'poppler_3_1':
            return out_dict
        if "php" in benchmark:
            values = {fuzzer: [float(n) for n in data[fuzzer][benchmark]] for fuzzer in fuzzers if fuzzer != "windranger"}
        else:
            values = {fuzzer: [float(n) for n in data[fuzzer][benchmark]] for fuzzer in fuzzers}
        max_worst_than = 0
        max_worst_fuzzer = None
        median_worst_values = 0
        tie = False
        for fuzzer in values:
            p_values = [mannwhitneyu(values[fuzzer], values[other], alternative=alternative).pvalue for other in values.keys() if other != fuzzer]
            num_siggy_worse = len([val for val in p_values if val < 0.05])
            if num_siggy_worse >= max_worst_than:
                if num_siggy_worse > max_worst_than:
                    tie = False
                tie = tie or (median(values[fuzzer]) == median_worst_values)
                max_worst_fuzzer = fuzzer
                max_worst_than = num_siggy_worse
                median_worst_values = median(values[fuzzer])
        if max_worst_fuzzer is not None and max_worst_than >= len(fuzzers)/2 and not tie:
            out_dict[benchmark] = max_worst_fuzzer
    return out_dict


def write_table_with_fuzzers(fuzzers, target_coverage = False):
    """
    Writes a LaTeX table where:
    - first column is the driver name
    - second column is the number of seeds, in k (if print_seeds)
    - next len(fuzzers) columns are the median execs for each fuzzer
    - next len(fuzzers) columns are the median real fuzz time for each fuzzer
    :param fuzzers: list of fuzzers to consider
    :param print_seeds: whether or not to print
    :param target_coverage: whether to process main coverage or only the target
    :return: none, prints to studout
    """
    if len(fuzzers) == 0:
        print("nothing to see here")
    highlight_text = "\\underline"

    data = {}
    with open(os.path.join(BASE_RESULTS_DIR, 'processed_target_coverage.csv' if target_coverage
                else 'processed_coverage.csv'), 'r') as f:
        for line in f:
            split_line = line.strip().split(',')
            fuzzer = split_line[0]
            benchmark = split_line[1]
            observations = split_line[2:]
            if fuzzer not in data:
                data[fuzzer] = {}
            data[fuzzer][benchmark] = observations

    to_highlight = retrieve_lowest_or_highest_for_each_benchmark(data, "highest", target_coverage)
    how_many_highlights_per_fuzzer = {fuzzer: len([v for v in to_highlight.values() if v == fuzzer]) for fuzzer in fuzzers}
    print(f"Number of times highlighted: {how_many_highlights_per_fuzzer}", file=sys.stderr)

    # _target_coverage.csv is in 0-1 range, processed_coverage.csv is percentages
    scale = 100 if target_coverage else 1
    for benchmark in data[next(iter(data))].keys():
        median_always_zero = True
        # Print the first two columns first
        out_str = benchmark.replace("_", "\\_")
        # Now print all the median execs columns
        fuzzer_to_highlight = to_highlight.get(benchmark, "")
        for fuzzer in fuzzers:
            # PHP is missing off windranger
            if benchmark not in data[fuzzer]:
                out_str += f"& $\\times$ "
                continue
            values_as_floats = [float(e)*scale if e != '-' else e for e in data[fuzzer][benchmark]]
            if '-' in values_as_floats:
                median_always_zero = False
                rendered_value = '-'
            else:
                median_value = median(values_as_floats)
                median_always_zero = median_always_zero and (median_value == 0)
                rendered_value = f"{median_value:.2f}"
            if fuzzer == fuzzer_to_highlight:
                out_str += "& "+ highlight_text +"{" + rendered_value +"}"
            else:
                out_str += f"& {rendered_value} "
        out_str += "\\\\"
        if not median_always_zero:
            print(out_str)

if __name__ == "__main__":
    print("=================median total project coverage====================")
    write_table_with_fuzzers(['afl', 'aflpp', 'libfuzzer', 'aflgo', 'aflgoexp', 'ffd', 'windranger', 'tunefuzz'])
    print("==============median (non-zero) target file coverage==============")
    write_table_with_fuzzers(['afl', 'aflpp', 'libfuzzer', 'aflgo', 'aflgoexp', 'ffd', 'windranger', 'tunefuzz'], True)