import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from statistical_test import *

BASE_SURVIVAL_DIR="../survival-results"
BASE_RESULTS_DIR= "../main-results"

fuzzers = ['afl', 'aflplusplus', 'libfuzzer', 'aflgo', 'aflgoexp', 'ffd', 'windranger', 'tunefuzz']


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
                    if len(it_data["reached"]) > 0:
                        # each benchmark in our case is a single bug injected
                        assert(len(it_data["reached"]) == 1)
                        # so it_data["reached"] looks like {bug_id: time_reached}
                        reached_arr.append(next(iter(it_data["reached"].items()))[1])
                    if len(it_data["triggered"]) > 0:
                        # each benchmark in our case is a single bug injected
                        assert(len(it_data["triggered"]) == 1)
                        # so it_data["triggered"] looks like {bug_id: time_triggered}
                        triggered_arr.append(next(iter(it_data["triggered"].items()))[1])
            reached_results[fuzzer_name][benchmark] = reached_arr
            triggered_results[fuzzer_name][benchmark] = triggered_arr
    return reached_results, triggered_results


def get_result_arrays(with_inst):
    if with_inst:
        postfix="-inst.json"
    else:
        postfix=".json"
    total_reached = {}
    total_triggered = {}
    for fuzzer in fuzzers:
        file_name=f"{BASE_RESULTS_DIR}/{fuzzer}{postfix}"
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
def format_survival_time_tables(with_inst: bool):
    survival_dfs = {}
    if with_inst:
        postfix="-inst-survival.csv"
    else:
        postfix="-survival.csv"

    for fuzzer in fuzzers:
        full_path = os.path.join(BASE_SURVIVAL_DIR, f"{fuzzer}{postfix}")
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
    afl_df = survival_dfs['afl'][['target', 'survival_time_reached', 'survival_time_triggered']]
    merged_df = afl_df.set_index('target').rename(columns={'survival_time_reached': 'afl_time_r', 'survival_time_triggered': 'afl_time_t'})

    for i in range(1, len(fuzzers)):
        df = survival_dfs[fuzzers[i]][['target', 'survival_time_reached', 'survival_time_triggered']]
        df_renamed = df.set_index('target').rename(columns={'survival_time_reached': f'{fuzzers[i]}_time_r', 'survival_time_triggered': f'{fuzzers[i]}_time_t'})
        # outer join
        merged_df = merged_df.merge(df_renamed, on='target', how='outer')

    merged_df = merged_df.round(0)
    merged_df = merged_df.fillna(' ').astype(str)
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



#### OLD
def merge_bug_results(bug_result_output_dir, bug_result_json_name):
    os.makedirs(bug_result_output_dir, exist_ok=True)
    bug_result_file_name = os.path.join(bug_result_output_dir, bug_result_json_name)
    # merge all bug counts into one file
    num_trial= 10
    results = {
        'afl': {'reached': [0]*num_trial, 'triggered': [0]*num_trial},
        'aflplusplus': {'reached':[0]*num_trial, 'triggered': [0]*num_trial},
        'libfuzzer': {'reached': [0]*num_trial, 'triggered': [0]*num_trial},
        'aflgo': {'reached': [0]*num_trial, 'triggered': [0]*num_trial},
        'aflgoexp': {'reached': [0]*num_trial, 'triggered': [0]*num_trial},
        'ffd': {'reached': [0]*num_trial, 'triggered': [0]*num_trial},
        'tunefuzz': {'reached': [0]*num_trial, 'triggered': [0]*num_trial}
    }

    file_paths = ['../process_data_tosem/bug_analysis/afl_results.json', 
                  '../process_data_tosem/bug_analysis/aflplusplus_results.json',
                  '../process_data_tosem/bug_analysis/libfuzzer_results.json',
                  '../process_data_tosem/bug_analysis/aflgo_results.json', 
                  '../process_data_tosem/bug_analysis/ffd_results.json',
                  '../process_data_tosem/bug_analysis/tunefuzz_results.json']
    
    for path in file_paths:
        results = get_time_to_bug(path, results)

    # special workaround for aflgoexp as its fuzzer name is recorded as aflgo in the fuzzing data 
    results = get_time_to_bug('../process_data_tosem/bug_analysis/aflgoexp_results.json', results, 'aflgoexp')
    print(results)

    with open(bug_result_file_name, 'w') as json_file:
        json.dump(results, json_file)
    
    return json_file

    
def format_num_bug_and_survival_time_tables(dir_path, fuzzers):
    num_bug_result = {}
    bug_analysis_dfs = {}

    for file in os.listdir(dir_path):
        full_path = os.path.join(dir_path, file)
        if os.path.isfile(full_path) and 'survival_analysis' in full_path:
            df = pd.read_csv(full_path)
            fuzzer_name = file.split('_')[0]
            num_bug_result[fuzzer_name] = [int(df['survival_time_reached'].count()), int(df['survival_time_triggered'].count())]
            bug_analysis_dfs[fuzzer_name] = df

    # format the table for the number of bugs 
    num_bug_formatted_latex = ''
    for fuzzer in fuzzers:
        num_bug_formatted_latex += ' & '.join(map(str, num_bug_result[fuzzer])) + ' & '
    # remove the trailing &
    num_bug_formatted_latex = num_bug_formatted_latex.rstrip(' & ')
    print('Formatted number of bugs reached and triggered:')
    print(num_bug_formatted_latex)

    # format the table for the survival time
    # merge all dfs together with the selected columns
    afl_df = bug_analysis_dfs['afl'][['target', 'survival_time_reached', 'survival_time_triggered']]
    merged_df = afl_df.set_index('target').rename(columns={'survival_time_reached': 'afl_time_r', 'survival_time_triggered': 'afl_time_t'})

    for i in range(1, len(fuzzers)):
        df = bug_analysis_dfs[fuzzers[i]][['target', 'survival_time_reached', 'survival_time_triggered']]
        df_renamed = df.set_index('target').rename(columns={'survival_time_reached': f'{fuzzers[i]}_time_r', 'survival_time_triggered': f'{fuzzers[i]}_time_t'})
        # outer join
        merged_df = merged_df.merge(df_renamed, on='target', how='outer')  

    merged_df = merged_df.round(1)
    merged_df = merged_df.fillna(' ').astype(str)
    merged_df = merged_df.sort_index().reset_index()
    merged_df['target'] = merged_df['target'].apply(lambda val: val.replace('_', '\_'))

    print('Formatted survival time:')
    for row in merged_df.apply(lambda x: x.map(str).str.cat(sep=' & '), axis=1):
        print(row + ' \\\\')
    return merged_df


def plot_sensitivity_results(output_dir, output_file_name):
    aflgo_original_df = pd.read_csv('../process_data_tosem/bug_analysis/aflgo_survival_analysis')
    aflgoexp_original_df = pd.read_csv('../process_data_tosem/bug_analysis/aflgoexp_survival_analysis')
    ffd_original_df = pd.read_csv('../process_data_tosem/bug_analysis/ffd_survival_analysis')

    df = pd.read_csv('../process_data_tosem/sensitivity/bug_analysis/sensitivity_survival_analysis')

    aflgo_sensitivity_df = df[ df['fuzzer'] == 'aflgo'].reset_index()
    aflgoexp_sensitivity_df = df[ df['fuzzer'] == 'aflgoexp'].reset_index()
    ffd_sensitivity_df = df[ df['fuzzer'] == 'ffd'].reset_index()

    sensitivity_fuzzers = ['aflgo', 'aflgoexp', 'ffd']
    reached_feature_name = 'survival_time_reached'
    triggered_feature_name = 'survival_time_triggered'

    original_reached = [aflgo_original_df[reached_feature_name].notna().sum(), aflgoexp_original_df[reached_feature_name].notna().sum(), ffd_original_df[reached_feature_name].notna().sum()]
    original_triggered = [aflgo_original_df[triggered_feature_name].notna().sum(), aflgoexp_original_df[triggered_feature_name].notna().sum(), ffd_original_df[triggered_feature_name].notna().sum()]

    sensitivity_reahced = [aflgo_sensitivity_df[reached_feature_name].notna().sum(), aflgoexp_sensitivity_df[reached_feature_name].notna().sum(), ffd_sensitivity_df[reached_feature_name].notna().sum()]
    sensitivity_triggered = [aflgo_sensitivity_df[triggered_feature_name].notna().sum(), aflgoexp_sensitivity_df[triggered_feature_name].notna().sum(), ffd_sensitivity_df[triggered_feature_name].notna().sum()]

    index = ['aflgo', 'aflgoexp', 'ffd']
    sensitivity_df_reached = pd.DataFrame({'original': original_reached, 'sensitivity': sensitivity_reahced}, index=index)
    ax =  sensitivity_df_reached.plot.bar(rot=0)
    plt.savefig('../process_data_tosem/figures/sensitivity_num_of_bug_reached.png') 

    sensitivity_df_triggered = pd.DataFrame({'original': original_triggered, 'sensitivity': sensitivity_triggered}, index=index)
    ax = sensitivity_df_triggered.plot.bar(rot=0)
    output_path = os.path.join(output_dir, output_file_name)
    plt.savefig(output_path) 


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

make_reached_triggered_bug_barplots()
print("==============Survival Time Without Instrumentation ===============")
format_survival_time_tables(False)
print("==============Survival Time With Instrumentation ===============")
format_survival_time_tables(True)
print("==============Information on Exception Cases ===============")
print_info_about_reaching_and_triggering_probs()
print("==============AFL vs TuneFuzz Reaching Times==============")
AFL_vs_TuneFuzz_mean_reaching_time_with_inst()