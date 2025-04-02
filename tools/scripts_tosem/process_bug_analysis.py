import os 
import statistics
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statistical_test import *


# outdated as we reformatted the sensitivity log
# we do not plot the stdev in this func as the values here are the maximum number of bugs reached/triggered instead of mean values
# e.g., plot_sensitivity_results('../process_data_tosem/original_experiments/figures', 'sensitivity_max_num_of_bug_reached.png', 'sensitivity_max_num_of_bug_triggered.png')
def plot_sensitivity_results(output_dir, reached_fig_name, triggered_fig_name):
    aflgo_original_df = pd.read_csv('../process_data_tosem/original_experiments/bug_analysis/aflgo_survival_analysis')
    aflgoexp_original_df = pd.read_csv('../process_data_tosem/original_experiments/bug_analysis/aflgoexp_survival_analysis')
    ffd_original_df = pd.read_csv('../process_data_tosem/original_experiments/bug_analysis/ffd_survival_analysis')

    df = pd.read_csv('../process_data_tosem/original_experiments/sensitivity/bug_analysis/sensitivity_survival_analysis')

    aflgo_sensitivity_df = df[ df['fuzzer'] == 'aflgo'].reset_index()
    aflgoexp_sensitivity_df = df[ df['fuzzer'] == 'aflgoexp'].reset_index()
    ffd_sensitivity_df = df[ df['fuzzer'] == 'ffd'].reset_index()

    sensitivity_fuzzers = ['aflgo', 'aflgoexp', 'ffd']
    reached_feature_name = 'survival_time_reached'
    triggered_feature_name = 'survival_time_triggered'

    original_reahced = [aflgo_original_df[reached_feature_name].notna().sum(), aflgoexp_original_df[reached_feature_name].notna().sum(), ffd_original_df[reached_feature_name].notna().sum()]
    original_triggered = [aflgo_original_df[triggered_feature_name].notna().sum(), aflgoexp_original_df[triggered_feature_name].notna().sum(), ffd_original_df[triggered_feature_name].notna().sum()]

    sensitivity_reahced = [aflgo_sensitivity_df[reached_feature_name].notna().sum(), aflgoexp_sensitivity_df[reached_feature_name].notna().sum(), ffd_sensitivity_df[reached_feature_name].notna().sum()]
    sensitivity_triggered = [aflgo_sensitivity_df[triggered_feature_name].notna().sum(), aflgoexp_sensitivity_df[triggered_feature_name].notna().sum(), ffd_sensitivity_df[triggered_feature_name].notna().sum()]

    index = ['aflgo', 'aflgoexp', 'ffd']
    sensitivity_df_reached = pd.DataFrame({'original': original_reahced, 'sensitivity': sensitivity_reahced}, index=index)


    fig, ax = plt.subplots(figsize=(10, 6))
    sensitivity_df_reached.plot.bar(rot=0, ax=ax)
    ax.legend(loc='best')
    output_path = os.path.join(output_dir, reached_fig_name)
    plt.savefig(output_path) 

    sensitivity_df_triggered = pd.DataFrame({'original': original_triggered, 'sensitivity': sensitivity_triggered}, index=index)
    fig, ax = plt.subplots(figsize=(10, 6))
    sensitivity_df_triggered.plot.bar(rot=0, ax=ax)
    ax.legend(loc='best')
    output_path = os.path.join(output_dir, triggered_fig_name)
    plt.savefig(output_path) 


# outdated as we created new plots for better comparison
# plot the mean/stdev number of bugs reached and triggered for all fuzzers 
# e.g., plot_bug_for_all_fuzzers(after_instrumentation_results, '../process_data_tosem/original_experiments/figures', 'num_of_bug_reached_after_instrumentation_all_fuzzers.png', 'num_of_bug_triggered_after_instrumentation_all_fuzzers.png')
def plot_bug_for_all_fuzzers(results, output_dir, file_name_reached, file_name_triggered):
    fuzzer_lst = []
    reached_mean = []
    triggered_mean = []
    reached_stdev = []
    triggered_stdev = []

    for fuzzer, f_data in results.items():
        fuzzer_lst.append(fuzzer)
        reached_mean.append(statistics.mean(f_data['reached']))
        triggered_mean.append(statistics.mean(f_data['triggered']))
        reached_stdev.append(statistics.stdev(f_data['reached']))
        triggered_stdev.append(statistics.stdev(f_data['triggered']))
        
    print(reached_mean)
    print(triggered_mean)
    plt.figure(figsize=(8, 6))
    plt.bar(x=fuzzer_lst, height=reached_mean, yerr=reached_stdev)
    plt.xlabel('Fuzzer')
    plt.ylabel('Number of Bugs Reached')
    output_path = os.path.join(output_dir, file_name_reached)
    plt.savefig(output_path, format="png", dpi=300)

    plt.clf()

    plt.figure(figsize=(8, 6))
    plt.bar(x=fuzzer_lst, height=triggered_mean, yerr=triggered_stdev)
    plt.xlabel('Fuzzer')
    plt.ylabel('Number of Bugs Triggered')
    output_path = os.path.join(output_dir, file_name_triggered)
    plt.savefig(output_path, format="png", dpi=300)


def process_bug_results_without_instrumentation_time(output_file_path):
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

    file_paths = ['../process_data_tosem/original_experiments/bug_analysis/afl_results.json', 
                  '../process_data_tosem/original_experiments/bug_analysis/aflplusplus_results.json',
                  '../process_data_tosem/original_experiments/bug_analysis/libfuzzer_results.json',
                  '../process_data_tosem/original_experiments/bug_analysis/aflgo_results.json', 
                  '../process_data_tosem/original_experiments/bug_analysis/ffd_results.json',
                  '../process_data_tosem/original_experiments/bug_analysis/tunefuzz_results.json']
    
    for path in file_paths:
        results = get_time_to_bug(path, results)

    # special workaround for aflgoexp as its fuzzer name is recorded as aflgo in the fuzzing data 
    results = get_time_to_bug('../process_data_tosem/original_experiments/bug_analysis/aflgoexp_results.json', results, 'aflgoexp')

    with open(output_file_path, 'w') as json_file:
        json.dump(results, json_file)
    
    return json_file


def process_bug_results_without_instrumentation_time_sensitivity(output_file_path):
    # merge all bug counts into one file
    num_trial= 10
    results = {
        'aflgo': {'reached': [0]*num_trial, 'triggered': [0]*num_trial},
        'aflgoexp': {'reached': [0]*num_trial, 'triggered': [0]*num_trial},
        'ffd': {'reached': [0]*num_trial, 'triggered': [0]*num_trial}
    }

    file_paths = ['../process_data_tosem/original_experiments/bug_analysis/aflgo_results.json', 
                  '../process_data_tosem/original_experiments/bug_analysis/ffd_results.json']
    
    for path in file_paths:
        results = get_time_to_bug(path, results)

    # special workaround for aflgoexp as its fuzzer name is recorded as aflgo in the fuzzing data 
    results = get_time_to_bug('../process_data_tosem/original_experiments/bug_analysis/aflgoexp_results.json', results, 'aflgoexp')

    with open(output_file_path, 'w') as json_file:
        json.dump(results, json_file)
    
    return json_file


def get_instrumentation_time_for_all_fuzzers(fuzzers):
    instrumentation_time_dict = dict.fromkeys(fuzzers, {})

    for fuzzer in fuzzers:
        bug_rt_file_path = f'../process_data_tosem/original_experiments/bug_analysis/{fuzzer}_survival_analysis'
        instrumentation_time_file_path = f'../process_data_tosem/original_experiments/build_time/{fuzzer}_build_time'

        bug_rt_df = pd.read_csv(bug_rt_file_path)
        instrumentation_time_df = pd.read_csv(instrumentation_time_file_path)

        instrumentation_time_df['time'] = instrumentation_time_df['time'].apply(lambda x: x.strip('s')).astype(float)
        rt_benchmarks = bug_rt_df['target'].values

        for benchmark in rt_benchmarks:
            print(fuzzer, benchmark)
            instrumentation_time = instrumentation_time_df.loc[instrumentation_time_df['benchmark'] == benchmark, 'time'].iloc[0]
            instrumentation_time_dict[fuzzer][benchmark] = instrumentation_time

    return instrumentation_time_dict


def process_bug_results_with_instrumentation_time(fuzzers, instrumentation_time_dict, output_file_path):
    with_instrumentation_time_results = {}
    for fuzzer in fuzzers:
        bug_result_file_path = f'../process_data_tosem/original_experiments/bug_analysis/{fuzzer}_results.json'
        with_instrumentation_time_results[fuzzer] = results_after_counting_instrumentation_time(fuzzer, bug_result_file_path, instrumentation_time_dict)
    
    with open(output_file_path, 'w') as json_file:
        json.dump(with_instrumentation_time_results, json_file)
    
    return json_file


def process_mean_stdev_for_num_of_bug_reached_and_triggered(results):
    fuzzers = []

    reached_mean = []
    triggered_mean = []

    reached_stdev = []
    triggered_stdev = []
    
    for fuzzer, f_data in results.items():
        fuzzers.append(fuzzer)

        reached_mean.append(statistics.mean(f_data['reached']))
        triggered_mean.append(statistics.mean(f_data['triggered']))

        reached_stdev.append(statistics.stdev(f_data['reached']))
        triggered_stdev.append(statistics.stdev(f_data['triggered']))

    processed_results = {
        'fuzzers': fuzzers,
        'reached_mean': reached_mean,
        'triggered_mean': triggered_mean,
        'reached_stdev': reached_stdev,
        'triggered_stdev': triggered_stdev
    }

    return processed_results


def plot_mean_num_of_bug_reached_and_triggered(results, output_path):
    fuzzers = results['fuzzers']
    # plotting
    x = np.arange(len(fuzzers)) 
    # the width of the bars
    width = 0.4
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    attributes = ['reached', 'triggered']

    for attribute in attributes:
        offset = width * multiplier
        mean_attribute = f'{attribute}_mean'
        mean_measurement = results[mean_attribute]
        stdev_measurement = results[f'{attribute}_stdev']
        rects = ax.bar(x=(x + offset), height=mean_measurement, width=width, yerr=stdev_measurement, label=mean_attribute)
        ax.bar_label(rects, padding=2)
        multiplier += 1

    ax.set_ylabel('Number of Bugs')
    ax.set_xticks(x + width, fuzzers)
    ax.legend(loc='upper left', ncols=2)
    ax.set_ylim(0, 18)
    ax.set_ylim(0, 18)
    plt.savefig(output_path, format="png", dpi=300)


def format_num_bug_and_survival_time_tables(dir_path, fuzzers, instrumentation_time_dict):
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


    # merge all dfs together with the selected columns
    afl_df = bug_analysis_dfs['afl'][['target', 'survival_time_reached', 'survival_time_triggered']]
    merged_df = afl_df.set_index('target').rename(columns={'survival_time_reached': 'afl_time_r', 'survival_time_triggered': 'afl_time_t'})
    for i in range(1, len(fuzzers)):
        df = bug_analysis_dfs[fuzzers[i]][['target', 'survival_time_reached', 'survival_time_triggered']]
        df_renamed = df.set_index('target').rename(columns={'survival_time_reached': f'{fuzzers[i]}_time_r', 'survival_time_triggered': f'{fuzzers[i]}_time_t'})
        # outer join
        merged_df = merged_df.merge(df_renamed, on='target', how='outer')  

    print(merged_df)

    # formatting
    format_and_print_survival_analysis_table(merged_df)

    # count the instrumentation time
    for index, row in merged_df.iterrows():
        for fuzzer in fuzzers:
            r_attribute_name = f'{fuzzer}_time_r'
            t_attribute_name = f'{fuzzer}_time_t'
            instrumentation_time = instrumentation_time_dict[fuzzer][index]
            merged_df.loc[index, r_attribute_name] = row[r_attribute_name] + instrumentation_time
            merged_df.loc[index, t_attribute_name] = row[t_attribute_name] + instrumentation_time
    print(merged_df)

    # formatting
    format_and_print_survival_analysis_table(merged_df)


def format_and_print_survival_analysis_table(df):
    # formatting
    formatted_df = df.round(1)
    formatted_df = formatted_df.fillna(' ').astype(str)
    formatted_df = formatted_df.sort_index().reset_index()
    formatted_df['target'] = formatted_df['target'].apply(lambda val: val.replace('_', '\_'))

    print('Formatted survival time:')
    for row in formatted_df.apply(lambda x: x.map(str).str.cat(sep=' & '), axis=1):
        print(row + ' \\\\')



if __name__ == '__main__':
    #fuzzers = ['aflgo', 'aflgoexp', 'ffd']
    fuzzers = ['afl', 'aflplusplus', 'libfuzzer', 'aflgo', 'aflgoexp', 'ffd', 'tunefuzz']
    # prepare folder
    num_of_bug_output_dir = '../process_data_tosem/original_experiments/figures'
    os.makedirs(num_of_bug_output_dir, exist_ok=True)

    # prepare file name
    without_instrumentation_time_file_name = 'without_instrumentation_time_num_of_bug_results.json'
    without_instrumentation_time_file_path = os.path.join(num_of_bug_output_dir, without_instrumentation_time_file_name)

    # process the bug analysis result without instrumentation time
    process_bug_results_without_instrumentation_time(without_instrumentation_time_file_path)
    # process_bug_results_without_instrumentation_time_sensitivity(without_instrumentation_time_file_path)

    # read the bug analysis result without instrumentation time
    with open(without_instrumentation_time_file_path, 'r') as json_file:
        without_instrumentation_time_results = json.load(json_file)
    # print(without_instrumentation_time_results)

    # plot the heatmaps for the number of bugs reached and triggered
    p_matrix_reached = get_p_val_for_num_bug(without_instrumentation_time_results, fuzzers, 'reached', 'two-sided', False)
    p_matrix_triggered = get_p_val_for_num_bug(without_instrumentation_time_results, fuzzers, 'triggered', 'two-sided', False)
    p_val_heatmap_for_num_bug(p_matrix_reached, fuzzers, '../process_data_tosem/original_experiments/figures/num_bug_r_wo_instrumentation_time_two_sided.png')
    p_val_heatmap_for_num_bug(p_matrix_triggered, fuzzers, '../process_data_tosem/original_experiments/figures/num_bug_t_wo_instrumentation_time_two_sided.png')

    # process instrumentation time for all fuzzers
    instrumentation_time_dict = get_instrumentation_time_for_all_fuzzers(fuzzers)
    # print(instrumentation_time_dict)

    # process the bug analysis result with instrumentation time
    with_instrumentation_time_file_name = 'with_instrumentation_time_num_of_bug_results.json'
    with_instrumentation_time_file_path = os.path.join(num_of_bug_output_dir, with_instrumentation_time_file_name)
    process_bug_results_with_instrumentation_time(fuzzers, instrumentation_time_dict, with_instrumentation_time_file_path)
    
    # read the bug analysis result with instrumentation time
    with open(with_instrumentation_time_file_path, 'r') as json_file:
        with_instrumentation_time_results = json.load(json_file)
    # print(with_instrumentation_time_results)

    # plot the heatmaps for the number of bugs reached and triggered
    p_matrix_reached_w_instrumentation_time = get_p_val_for_num_bug(with_instrumentation_time_results, fuzzers, 'reached', 'two-sided', False)
    p_matrix_triggered_w_instrumentation_time = get_p_val_for_num_bug(with_instrumentation_time_results, fuzzers, 'triggered', 'two-sided', False)
    p_val_heatmap_for_num_bug(p_matrix_reached_w_instrumentation_time, fuzzers, '../process_data_tosem/original_experiments/figures/num_bug_r_w_instrumentation_time_two_sided.png')
    p_val_heatmap_for_num_bug(p_matrix_triggered_w_instrumentation_time, fuzzers, '../process_data_tosem/original_experiments/figures/num_bug_t_w_instrumentation_time_two_sided.png')

    # process mean and stdev
    processed_without_instrumentation_time_results = process_mean_stdev_for_num_of_bug_reached_and_triggered(without_instrumentation_time_results)
    processed_with_instrumentation_time_results = process_mean_stdev_for_num_of_bug_reached_and_triggered(with_instrumentation_time_results)

    # Mean Number of Bugs Reached and Triggered without Instrumentation Time
    plot_mean_num_of_bug_reached_and_triggered(processed_without_instrumentation_time_results, '../process_data_tosem/original_experiments/figures/mean_num_of_bug_rt_wo_instrumentation_time.png')
    # Mean Number of Bugs Reached and Triggered with Instrumentation Time
    plot_mean_num_of_bug_reached_and_triggered(processed_with_instrumentation_time_results, '../process_data_tosem/original_experiments/figures/mean_num_of_bug_rt_w_instrumentation_time.png')

    # print out the latex tables for survival time analysis
    format_num_bug_and_survival_time_tables('../process_data_tosem/original_experiments/bug_analysis', fuzzers, instrumentation_time_dict)
