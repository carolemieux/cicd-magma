import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import json
import numpy as np
from statistics import mean, geometric_mean
from scipy.stats import mannwhitneyu

BASE_SURVIVAL_DIR= "../tosem-results/survival-results"
BASE_SURVIVAL_SENSITIVITY_DIR= "../tosem-results/survival-sensitivity-results"
BASE_RESULTS_DIR= "../tosem-results/main-results"
BASE_SENSITIVITY_RESULTS_DIR= "../tosem-results/sensitivity-results"

fuzzers = ['afl', 'aflplusplus', 'libfuzzer', 'aflgo', 'aflgoexp', 'ffd', 'windranger', 'tunefuzz']
sensitivity_fuzzers = ['aflgo', 'aflgoexp', 'ffd', 'windranger']

# adapted from survival_analysis.py
# returns results which map a fuzzer name, benchmakr to times the bugs reached
# and another which maps a fuzzer name, benchmakr to times the to the bugs triggered
def time_r_t_per_bug(file_path, fuzzer_name):
    reached_results = {fuzzer_name: {}}
    triggered_results = {fuzzer_name: {}}
    with open(file_path, 'r') as file:
        data = json.load(file).get('results', {})
    for fuzzer, f_data in data.items():
        for benchmark, b_data in f_data.items():
            reached_arr = []
            triggered_arr = []
            assert len(b_data) == 1 # check only one fuzz target
            for fuzz_target, ft_data in b_data.items():
                for iteration, it_data in ft_data.items():
                    if len(it_data.get("reached",[])) > 0:
                        # each benchmark in our case is a single bug injected
                        assert(len(it_data["reached"]) == 1)
                        # so it_data["reached"] looks like {bug_id: time_reached}
                        reached_arr.append(next(iter(it_data["reached"].items()))[1])
                    if len(it_data.get("triggered",[])) > 0:
                        # each benchmark in our case is a single bug injected
                        assert(len(it_data["triggered"]) == 1)
                        # so it_data["triggered"] looks like {bug_id: time_triggered}
                        triggered_arr.append(next(iter(it_data["triggered"].items()))[1])
            reached_results[fuzzer_name][benchmark] = reached_arr
            triggered_results[fuzzer_name][benchmark] = triggered_arr
    return reached_results, triggered_results


def get_result_arrays(with_inst, sensitivity=False):
    """
    Mappings of fuzzer -> targets -> results
    :param with_inst:
    :param sensitivity:
    :return:
    """
    if with_inst:
        postfix="-inst.json"
    else:
        postfix=".json"
    total_reached = {}
    total_triggered = {}
    for fuzzer in (sensitivity_fuzzers if sensitivity else fuzzers):
        file_name=f"{BASE_SENSITIVITY_RESULTS_DIR if sensitivity else BASE_RESULTS_DIR}/{fuzzer}{postfix}"
        reached, triggered = time_r_t_per_bug(file_name,fuzzer)
        total_reached[fuzzer] = reached[fuzzer]
        total_triggered[fuzzer] = triggered[fuzzer]
    return total_reached, total_triggered

# Get fuzzer -> mean # of bugs reached/triggered over all benchmarks, all runs
# with_inst: boolean, include instrumentation time
def mean_reached_triggered(with_inst):
    # both of those are maps of fuzzer --> benchmark --> arrays
    total_reached, total_triggered = get_result_arrays(with_inst)
    # incomprehensible list/dict comprenenshions: takes the sum of length of
    # all those arrays, essentialy flattening over all benchmarks
    mean_reached = {fuzzer: sum([len(total_reached[fuzzer][bench]) for bench in total_reached[fuzzer]])/10 for fuzzer in total_reached}
    mean_triggered = {fuzzer: sum([len(total_triggered[fuzzer][bench]) for bench in total_reached[fuzzer]])/10 for fuzzer in total_triggered}
    return mean_reached, mean_triggered

def AFL_vs_TuneFuzz_mean_reaching_time_with_inst():

    postfix="-inst-survival.csv"

    full_path = os.path.join(BASE_SURVIVAL_DIR, f"afl{postfix}")
    if os.path.isfile(full_path):
        try:
            df = pd.read_csv(full_path)
            afl_survival = df
        except:
            print(f"Cannot read {full_path}", file=sys.stderr)
            exit(1)
    else:
        print(f"Cannot find {full_path}", file=sys.stderr)
        exit(1)

    full_path = os.path.join(BASE_SURVIVAL_DIR, f"tunefuzz{postfix}")
    if os.path.isfile(full_path):
        try:
            df = pd.read_csv(full_path)
            tunefuzz_survival = df
        except:
            print(f"Cannot read {full_path}", file=sys.stderr)
            exit(1)
    else:
        print(f"Cannot find {full_path}", file=sys.stderr)
        exit(1)


    # mean of column `survival_time_reached`
    mean_afl_survival = afl_survival['survival_time_reached'].mean()
    mean_tunefuzz_survival = tunefuzz_survival['survival_time_reached'].mean()
    print(f"Mean survival time reached is {mean_afl_survival} for AFL, {mean_tunefuzz_survival} for TuneFuzz")

    mean_afl_survival = afl_survival['survival_time_triggered'].mean()
    mean_tunefuzz_survival = tunefuzz_survival['survival_time_triggered'].mean()
    print(f"Mean survival time triggered is {mean_afl_survival} for AFL, {mean_tunefuzz_survival} for TuneFuzz, over all benchmarks")
    print(f"AFL triggered survival time for openssl_20_4:", float(afl_survival.loc[afl_survival['target'] == "openssl_20_4"]['survival_time_triggered'].iloc[0]))
    print(f"TuneFuzz triggered survival time for openssl_20_4:", float(tunefuzz_survival.loc[tunefuzz_survival['target'] == "openssl_20_4"]['survival_time_triggered'].iloc[0]))
    afl_survival_filtered = afl_survival[afl_survival['target'] != "openssl_20_4"]
    tunefuzz_survival_filtered = tunefuzz_survival[tunefuzz_survival['target'] != "openssl_20_4"]
    print(f"Mean survival time triggered is {afl_survival_filtered['survival_time_triggered'].mean()} for AFL, {tunefuzz_survival_filtered['survival_time_triggered'].mean()} for TuneFuzz, excluding openssl_20_4")

# Print the mean survival time tables in Latex format
def format_survival_time_tables(with_inst: bool, sensitivity: bool = False, highlight = False):
    survival_dfs = {}
    if with_inst:
        postfix="-inst-survival.csv"
    else:
        postfix="-survival.csv"

    if sensitivity:
        my_fuzzers = sensitivity_fuzzers
    else:
        my_fuzzers = fuzzers

    for fuzzer in my_fuzzers:
        full_path = os.path.join(BASE_SURVIVAL_SENSITIVITY_DIR if sensitivity else BASE_SURVIVAL_DIR, f"{fuzzer}{postfix}")
        if os.path.isfile(full_path):
            try:
                df = pd.read_csv(full_path)
                survival_dfs[fuzzer]= df
            except:
                print(f"Cannot read {full_path}", file=sys.stderr)
                exit(1)
        else:
            print(f"Cannot find {full_path}", file=sys.stderr)
            exit(1)


    # format the table for the survival time
    # merge all dfs together with the selected columns

    # get the first one out to make the base dataframe
    first_idx = 'aflgo' if sensitivity else 'afl'
    afl_df = survival_dfs[first_idx][['target', 'survival_time_reached', 'survival_time_triggered']]
    merged_df = afl_df.set_index('target').rename(columns={'survival_time_reached': f'{first_idx}_time_r', 'survival_time_triggered': f'{first_idx}_time_t'})

    for i in range(1, len(my_fuzzers)):
        df = survival_dfs[my_fuzzers[i]][['target', 'survival_time_reached', 'survival_time_triggered']]
        df_renamed = df.set_index('target').rename(columns={'survival_time_reached': f'{my_fuzzers[i]}_time_r', 'survival_time_triggered': f'{my_fuzzers[i]}_time_t'})
        # outer join
        merged_df = merged_df.merge(df_renamed, on='target', how='outer')

    # figure out what to highlight
    if highlight == True and not sensitivity:
        total_reached, total_triggered = get_result_arrays(with_inst, sensitivity=sensitivity)
        uwave_reached = [( bench,f"{f}_time_r") for f in my_fuzzers for bench, v in total_reached[f].items() if 0< len(v) < 10]
        uwave_triggered = [( bench, f"{f}_time_t") for f in my_fuzzers for bench, v in total_triggered[f].items() if 0< len(v) < 10]
        uwave_idxs = uwave_reached + uwave_triggered
        # reached minimums
        colorbox_idxs = []
        for r_t in ['time_r', 'time_t']:
            for row_idx in range(len(merged_df)):
                reached_triggered_vals = merged_df.iloc[row_idx].iloc[[i for i, r in enumerate(merged_df) if r_t in r]]
                if reached_triggered_vals.isnull().all():
                    continue
                min_reached_in_row = reached_triggered_vals.min(skipna=True)
                if (reached_triggered_vals == min_reached_in_row).sum() > 1:
                    continue
                min_col_name = reached_triggered_vals.idxmin(skipna=True)
                colorbox_idxs.append((merged_df.index[row_idx],min_col_name))
    if sensitivity and highlight != False:
        uwave_idxs = []
        colorbox_idxs = highlight

    merged_df = merged_df.round(0)
    merged_df = merged_df.fillna(' ').astype(str)
    if highlight:
        for row, col in uwave_idxs:
            merged_df.loc[row, col] = "\\uwave{"+ merged_df.loc[row, col] + "}"
        for row, col in colorbox_idxs:
            merged_df.loc[row, col] = "\\colorbox{gray!20}{"+ merged_df.loc[row, col] + "}"

    merged_df = merged_df.sort_index().reset_index()
    merged_df['target'] = merged_df['target'].apply(lambda val: val.replace('_', '\_'))

    print('Formatted survival time:')
    for row in merged_df.apply(lambda x: x.map(str).str.cat(sep=' & '), axis=1):
        # although we rounded to 0 decimal points, the .0s are hanging around.
        # get rid of them.
        row = row.replace(".0", "")
        print(row + ' \\\\')
    return merged_df



# Generates barplots for the number of bugs reached and triggered per fuzzer
def make_reached_triggered_bug_barplots():
    # colourblind-friendly color palette (https://jfly.uni-koeln.de/color/)
    okabe_ito = [
        (0.0, 0.447, 0.698),  # blue
        (0.902, 0.624, 0.0),  # orange
        (0.0, 0.62, 0.451),   # green
        (0.941, 0.894, 0.259),# yellow
        (0.835, 0.369, 0.0),  # red
        (0.8, 0.475, 0.655),  # purple
        (0.337, 0.706, 0.914),# sky blue
        (0.0, 0.0, 0.0),      # black
    ]
    # subroutine to make input RGB colour x% darker
    # ChatGPT-Generated
    def darken_color(rgb, percent):
        """
        Darken an RGB color by a given percent.

        Parameters:
            rgb (tuple): (r, g, b) with values in [0, 1]
            percent (float): percentage to darken (e.g., 20 for 20%)

        Returns:
            tuple: darkened (r, g, b)
        """
        factor = 1 - percent / 100
        return tuple(max(0, c * factor) for c in rgb)

    colours = [okabe_ito[6], okabe_ito[0], okabe_ito[1], okabe_ito[4]]
    hatches = ["//", "//..", "\\\\", "\\\\.."]

    reached_w_o_inst, triggered_w_o_inst = mean_reached_triggered(False)
    reached_w_inst, triggered_w_inst = mean_reached_triggered(True)

    labels = list(reached_w_o_inst.keys())
    labels = ["AFL", "AFL++", "libFuzzer", "AFLGo", "AFLGoE", "FFD", "WindRanger", "TuneFuzz"]
    n_labels = len(labels)

    labelled_series = [("Reached, w/o instr. time", list(reached_w_o_inst.values())),
                       ("Reached, w. instr. time", list(reached_w_inst.values())),
                       ("Triggered, w/o instr. time", list(triggered_w_o_inst.values())),
                       ("Triggered, w. instr. time", list(triggered_w_inst.values()))]

    # We will cluster the four series together
    num_clusters = 4

    fig, ax = plt.subplots(figsize=(13, 4))
    bar_width = 0.3
    gap = 0.2

    n_series = len(labelled_series)
    total_width = n_series * bar_width

    group_positions = np.arange(n_labels)*(total_width+ gap)
    offsets = (np.arange(n_series) - (n_series-1)/2)*bar_width

    print(labelled_series)
    for i in range(n_series):
        bars = ax.bar(group_positions+offsets[i], labelled_series[i][1], bar_width,
               label=labelled_series[i][0], edgecolor=darken_color(colours[i],50), facecolor=colours[i], hatch=hatches[i])
        ax.bar_label(bars, padding=3, fontsize=8)

    ax.set_xticks(group_positions)
    ax.set_xticklabels(labels)
    ax.legend(loc='upper left', bbox_to_anchor=(0.21, 1), prop={'size': 9.5})
    ax.set_ylabel("Average Number of Bugs Reached/Triggered")
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig("./figures/reached_triggered_barplot.pdf")

# Print english sentences about the probabilities of reaching/triggering
# bugs that are not 0 or 1, or that differ with instrumentation.
def print_info_about_reaching_and_triggering_probs():
    # all are maps of fuzzer --> benchmark --> arrays
    total_w_o_reached, total_w_o_triggered = get_result_arrays(False)
    total_w_reached, total_w_triggered = get_result_arrays(True)
    # Reaching
    for fuzzer in total_w_o_reached:
        for bench in total_w_o_reached[fuzzer]:
            reached_array_w_o = total_w_o_reached[fuzzer][bench]
            reached_array_w = total_w_reached[fuzzer][bench]
            if 0 <len(reached_array_w_o) < 10:
                print(f"Fuzzer {fuzzer} reaches {bench} with prob {len(reached_array_w_o)/10} without instrumentation.")
            if 0< len(reached_array_w) < 10:
                print(f"Fuzzer {fuzzer} reaches {bench} with prob {len(reached_array_w)/10} with instrumentation.")
            if len(reached_array_w_o) != len(reached_array_w):
                print(f"Fuzzer {fuzzer} on {bench} reaches in {len(reached_array_w_o)} iterations without "
                      f"and {len(reached_array_w)} iterations with instrumentation.")
                print("The raw times w/o instrumentation:",reached_array_w_o)
    # Triggering
    for fuzzer in total_w_o_triggered:
        for bench in total_w_o_triggered[fuzzer]:
            triggered_array_w_o = total_w_o_triggered[fuzzer][bench]
            triggered_array_w = total_w_triggered[fuzzer][bench]
            if 0 < len(triggered_array_w_o) < 10:
                print(f"Fuzzer {fuzzer} triggers {bench} with prob {len(triggered_array_w_o)/10} without instrumentation.")
            if 0 < len(triggered_array_w)<  10:
                print(f"Fuzzer {fuzzer} triggers {bench} with prob {len(triggered_array_w)/10} with instrumentation.")
            if len(triggered_array_w_o) != len(triggered_array_w):
                print(f"Fuzzer {fuzzer} on {bench} triggers in {len(triggered_array_w_o)} iterations without "
                      f"and {len(triggered_array_w)} iterations with instrumentation.")
                print("The raw times w/o instrumentation:",triggered_array_w_o)


def compare_sensitivity_results(with_inst):
    orig_reached, orig_triggered = get_result_arrays(with_inst, False)
    sensitivity_reached, sensitivity_triggered = get_result_arrays(with_inst, True)
    # Print Stuff in human readable format
    for fuzzer in sensitivity_reached:
        for bench in sensitivity_reached[fuzzer]:
            sen_reached = sensitivity_reached[fuzzer][bench]
            or_reached= orig_reached[fuzzer][bench]
            if (sen_reached != or_reached):
                print(f"Sensitivity changes reached results for {fuzzer} on {bench}: before {or_reached} and after {sen_reached}")
                if len(sen_reached) == len(or_reached):
                    print(f"MWU-ne: {mannwhitneyu(or_reached, sen_reached, alternative='two-sided', method='exact').pvalue}, "
                          f"MWU-lt: {mannwhitneyu(or_reached, sen_reached, alternative='less', method='exact').pvalue}, "
                          f"MWU-gt: {mannwhitneyu(or_reached, sen_reached, alternative='greater', method='exact').pvalue}")
    for fuzzer in sensitivity_triggered:
        for bench in sensitivity_triggered[fuzzer]:
            sen_triggered = sensitivity_triggered[fuzzer][bench]
            or_triggered= orig_triggered[fuzzer][bench]
            if (sen_triggered != or_triggered):
                print(f"Sensitivity changes triggered results for {fuzzer} on {bench}: before {or_triggered} and after {sen_triggered}")
                if len(sen_triggered) == len(or_triggered):
                    print(f"MWU-ne: {mannwhitneyu(or_triggered, sen_triggered, alternative='two-sided', method='exact').pvalue}, "
                          f"MWU-lt: {mannwhitneyu(or_triggered, sen_triggered, alternative='less', method='exact').pvalue}, "
                          f"MWU-gt: {mannwhitneyu(or_triggered, sen_triggered, alternative='greater', method='exact').pvalue}")


    #
    # Make a Table that summarizes the above for the paper
    print("==================Table Comparing Sensitivity Results=================")
    # Helper function to check whether the two things are the same. if not,
    # do the mann whitney u test accordingly and give the p-value
    def test_and_give_p_value(orig,sensitivity, reached_or_triggered:str):
        def round_to_2(x):
            from math import floor, log10
            #return round(x, -int(floor(log10(abs(x))))+1)
            return f'{x:.{-int(floor(log10(x)))+1}f}'
        if len(orig) == 0 and len(sensitivity) == 0:
            return ""
        if orig == sensitivity:
            return ""
        if len(orig) == 0  and len(sensitivity)>0:
            return f"newly {reached_or_triggered} ({len(sensitivity)} iteration)"
        if len(orig) > 0  and len(sensitivity)==0:
            return f"no longer {reached_or_triggered}"
        if np.mean(orig) < np.mean(sensitivity):
            p = mannwhitneyu(orig, sensitivity, alternative='less').pvalue
            return f"{reached_or_triggered} {np.mean(sensitivity)-np.mean(orig)}s slower ($p={round_to_2(p)}$)"
        elif np.mean(orig) > np.mean(sensitivity):
            p = mannwhitneyu(orig, sensitivity, alternative='greater').pvalue
            return f"{reached_or_triggered} {np.mean(orig)-np.mean(sensitivity)}s faster ($p={round_to_2(p)}$)"

    # Gets d[fuzzer][benchmark] or returns []
    def get_or_empty(d, fuzzer,benchmark):
        if fuzzer in d:
            if benchmark in d[fuzzer]:
                return d[fuzzer][benchmark]
            else:
                return []
        else:
            return []

    benchmarks = sorted([s for s in sensitivity_reached['aflgo'].keys()])
    to_highlight_in_table = []
    for fuzzer in sensitivity_fuzzers:
        for bench in benchmarks:
            out = f"{fuzzer} & {bench}".replace('_','\\_')
            reached_original = get_or_empty(orig_reached,fuzzer,bench)
            reached_sensitive = get_or_empty(sensitivity_reached, fuzzer,bench)
            reached_res = test_and_give_p_value(reached_original, reached_sensitive, "reached")
            if reached_res:
                #out += f"&  {reached_res} & "
                to_highlight_in_table.append((bench, f"{fuzzer}_time_r"))
                print(out+f" & {reached_res}\\\\")
            #out += f" & {test_and_give_p_value(reached_original, reached_sensitive)}"

            triggered_original = get_or_empty(orig_triggered,fuzzer,bench)
            triggered_sensitive = get_or_empty(sensitivity_triggered, fuzzer,bench)
            triggered_res = test_and_give_p_value(triggered_original, triggered_sensitive, "triggered")
            if triggered_res:
                #out += f"&  {triggered_res} & "
                to_highlight_in_table.append((bench, f"{fuzzer}_time_t"))
                print(out+f" & {triggered_res}\\\\")
    return to_highlight_in_table


def print_instrumentation_time_changes_with_sensitivity():
    def get_instrumentation_time_dict(fuzzer, sensitivity):
        instrumentation_file_name = f'{fuzzer}-inst.csv'
        instrumentation_file_name = os.path.join(BASE_SENSITIVITY_RESULTS_DIR if sensitivity else BASE_RESULTS_DIR, instrumentation_file_name)
        ret_dict = {}
        with open(instrumentation_file_name) as f:
            for line in f:
                if fuzzer =='windranger' and 'php' in line:
                    continue
                bench, time = line.split(',')
                ret_dict[bench] = float(time)
        return ret_dict

    for fuzzer in sensitivity_fuzzers:
        orig_instr_times = get_instrumentation_time_dict(fuzzer, False)
        sens_instr_times = get_instrumentation_time_dict(fuzzer, True)
        print(f"{fuzzer} orig times: {mean([v for k,v in orig_instr_times.items() if k in sens_instr_times])} new times: {mean(sens_instr_times.values())}")
        times_differences = []
        value_differences = []
        for bench in sens_instr_times:
            times_differences.append(sens_instr_times[bench]/orig_instr_times[bench])
            value_differences.append(sens_instr_times[bench] - orig_instr_times[bench])
        print(f"For fuzzer: {fuzzer}, instrumentation is {geometric_mean(times_differences)}X slower, "
              f"or in absolute terms {mean(value_differences)}s slower on average over all benchmarks.")


#if __name__ == '__main__':

    # bug_result_output_dir = '../process_data_tosem/figures'
    # bug_result_json_name = 'num_of_bug_rt.json'
    # merge_bug_results(bug_result_output_dir, bug_result_json_name)
    #
    # # read the bug results and plot the heatmap
    # bug_result_file_name = os.path.join(bug_result_output_dir, bug_result_json_name)
    # with open(bug_result_file_name, 'r') as json_file:
    #     num_bug_results = json.load(json_file)
    # print(num_bug_results)
    #
    # fuzzers = ['afl', 'aflplusplus', 'libfuzzer', 'aflgo', 'aflgoexp', 'ffd', 'windranger', 'tunefuzz']
    #
    # p_matrix_reached = get_p_val_for_num_bug(num_bug_results, fuzzers, 'reached', 'greater', True)
    # p_matrix_triggered = get_p_val_for_num_bug(num_bug_results, fuzzers, 'triggered', 'greater', True)
    #
    # # plot the heatmaps for the number of bugs reached and triggered
    # p_val_heatmap_for_num_bug(p_matrix_reached, 'P Values for the Number of Bugs Reached', '../process_data_tosem/figures/num_bug_r_greater.png', fuzzers)
    # p_val_heatmap_for_num_bug(p_matrix_triggered, 'P Values for the Number of Bugs Triggered', '../process_data_tosem/figures/num_bug_t_greater.png', fuzzers)
    #
    # # print out the latex tables
    # format_num_bug_and_survival_time_tables('../process_data_tosem/bug_analysis', fuzzers)

    # # process sensitivity experiments
    # plot_sensitivity_results('../process_data_tosem/figures', 'sensitivity_num_of_bug_triggered.png')

if __name__ == "__main__":
    print("==============Mean Reached/Triggered Total Results (Makes Barplot)=========")
    make_reached_triggered_bug_barplots()
    print("==============Survival Time Without Instrumentation ===============")
    format_survival_time_tables(False, False, True)
    print("==============Survival Time With Instrumentation ===============")
    format_survival_time_tables(True, False, True)
    print("==============Information on Exception Cases ===============")
    print_info_about_reaching_and_triggering_probs()
    print("==============AFL vs TuneFuzz Reaching Times==============")
    AFL_vs_TuneFuzz_mean_reaching_time_with_inst()
    print("-----------------------Sensitivity------------------------")
    print("==============Comparative Times Without Instrumentation==================")
    to_highlight = compare_sensitivity_results(False)
    print("==============Survival Time Without Instrumentation, Sensitivity ===============")
    format_survival_time_tables(False, True, to_highlight)
    print("==============How does instrumentation time change with sensitivity?=============")
    print_instrumentation_time_changes_with_sensitivity()