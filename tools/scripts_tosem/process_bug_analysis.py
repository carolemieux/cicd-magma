import os 
import statistics
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statistical_test import *


def process_bug_results(fuzzers, num_trial, fuzzing_data_path, output_file_path, instrumentation_time_dict=None):
    results = {
        fuzzer: {'reached': [0]*num_trial, 'triggered': [0]*num_trial} for fuzzer in fuzzers
    }

    if instrumentation_time_dict:
        for fuzzer in fuzzers:
            file_path = f'{fuzzing_data_path}/{fuzzer}_results.json'
            get_time_to_bug_with_instrumentation_time(file_path, results, instrumentation_time_dict)
    else:
        for fuzzer in fuzzers:
            file_path = f'{fuzzing_data_path}/{fuzzer}_results.json'
            get_time_to_bug(file_path, results)
        
    with open(output_file_path, 'w') as json_file:
        json.dump(results, json_file)
    
    return json_file


def get_instrumentation_time_for_all_fuzzers(fuzzers, fuzzing_data_path):
    instrumentation_time_dict = dict.fromkeys(fuzzers, {})

    for fuzzer in fuzzers:
        bug_rt_file_path = f'{fuzzing_data_path}/bug_analysis/{fuzzer}_survival_analysis'
        instrumentation_time_file_path = f'{fuzzing_data_path}/build_time/{fuzzer}_build_time'

        bug_rt_df = pd.read_csv(bug_rt_file_path)
        instrumentation_time_df = pd.read_csv(instrumentation_time_file_path)

        instrumentation_time_df['time'] = instrumentation_time_df['time'].apply(lambda x: x.strip('s')).astype(float)
        rt_benchmarks = bug_rt_df['target'].values

        print(instrumentation_time_df)
        for benchmark in rt_benchmarks:
            print(fuzzer, benchmark)
            benchmark_time = instrumentation_time_df.loc[instrumentation_time_df['benchmark'] == benchmark, 'time']
            if benchmark_time.empty:
                instrumentation_time = np.inf
            else:
                instrumentation_time = instrumentation_time_df.loc[instrumentation_time_df['benchmark'] == benchmark, 'time'].iloc[0]
            instrumentation_time_dict[fuzzer][benchmark] = instrumentation_time
    return instrumentation_time_dict


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
    # width = 0.4
    width = 0.15
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
    base_fuzzer = fuzzers[0]
    base_df = bug_analysis_dfs[base_fuzzer][['target', 'survival_time_reached', 'survival_time_triggered']]
    merged_df = base_df.set_index('target').rename(columns={'survival_time_reached': f'{base_fuzzer}_time_r', 'survival_time_triggered': f'{base_fuzzer}_time_t'})
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


def plot_bug_analysis_results(fuzzers, numofbug_json_path, heatmap_output_path, numofbug_output_path):
    # read the bug analysis result without instrumentation time
    with open(numofbug_json_path, 'r') as json_file:
        numofbug_results = json.load(json_file)

    # plot the heatmaps for the number of bugs reached and triggered
    p_matrix_reached = get_p_val_for_num_bug(numofbug_results, fuzzers, 'reached', 'two-sided', False)
    p_matrix_triggered = get_p_val_for_num_bug(numofbug_results, fuzzers, 'triggered', 'two-sided', False)
    p_val_heatmap_for_num_bug_compact(p_matrix_reached, p_matrix_triggered, fuzzers, heatmap_output_path)
    
    # mean Number of Bugs Reached and Triggered without Instrumentation Time
    processed_numofbug_results = process_mean_stdev_for_num_of_bug_reached_and_triggered(numofbug_results)
    plot_mean_num_of_bug_reached_and_triggered(processed_numofbug_results, numofbug_output_path)


def plot_and_format_bug_analysis_results(fuzzers, data_path):
    figure_output_path = os.path.join(data_path, 'figures')
    bug_analysis_output_path = os.path.join(data_path, 'bug_analysis')
    os.makedirs(figure_output_path, exist_ok=True)
    os.makedirs(bug_analysis_output_path, exist_ok=True)

    numofbug_wo_instrumentation_output_path = os.path.join(figure_output_path, 'num_of_bugs_wo_instrumentation.json')
    heatmap_wo_instrumentation_output_path = os.path.join(figure_output_path, 'rt_num_bug_heatmap_wo_instrumentation.png')
    mean_stdev_bar_wo_instrumentation_output_path = os.path.join(figure_output_path, 'mean_stdev_num_bug_wo_instrumentation.png')

    numofbug_w_instrumentation_output_path = os.path.join(figure_output_path, 'num_of_bugs_w_instrumentation.json')
    heatmap_w_instrumentation_output_path = os.path.join(figure_output_path, 'rt_num_bug_heatmap_w_instrumentation.png')
    mean_stdev_bar_w_instrumentation_output_path = os.path.join(figure_output_path, 'mean_stdev_num_bug_w_instrumentation.png')


    # process the bug analysis result without instrumentation time
    process_bug_results(fuzzers, 10, bug_analysis_output_path, numofbug_wo_instrumentation_output_path)
    plot_bug_analysis_results(fuzzers, numofbug_wo_instrumentation_output_path, heatmap_wo_instrumentation_output_path, mean_stdev_bar_wo_instrumentation_output_path)


    # process instrumentation time for all fuzzers
    instrumentation_time_dict = get_instrumentation_time_for_all_fuzzers(fuzzers, data_path)
    print(instrumentation_time_dict)
    # process the bug analysis result with instrumentation time
    process_bug_results(fuzzers, 10, bug_analysis_output_path,  numofbug_w_instrumentation_output_path, instrumentation_time_dict)
    plot_bug_analysis_results(fuzzers, numofbug_w_instrumentation_output_path, heatmap_w_instrumentation_output_path, mean_stdev_bar_w_instrumentation_output_path)

    # print out the latex tables for survival time analysis
    format_num_bug_and_survival_time_tables(bug_analysis_output_path, fuzzers, instrumentation_time_dict)


if __name__ == '__main__':
    # fuzzers = ['afl', 'aflplusplus', 'libfuzzer', 'aflgo', 'aflgoexp', 'ffd', 'tunefuzz']
    # data_path = '../process_data_tosem/original_experiments'
    # plot_and_format_bug_analysis_results(fuzzers, data_path)

    sensitivity_fuzzers = ['aflgo', 'aflgoexp', 'ffd']
    sensitivity_data_path = '../process_data_tosem/sensitivity_experiments'
    plot_and_format_bug_analysis_results(sensitivity_fuzzers, sensitivity_data_path)
    