import os 
import statistics
import pandas as pd
import matplotlib.pyplot as plt
from statistical_test import *


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

    original_reahced = [aflgo_original_df[reached_feature_name].notna().sum(), aflgoexp_original_df[reached_feature_name].notna().sum(), ffd_original_df[reached_feature_name].notna().sum()]
    original_triggered = [aflgo_original_df[triggered_feature_name].notna().sum(), aflgoexp_original_df[triggered_feature_name].notna().sum(), ffd_original_df[triggered_feature_name].notna().sum()]

    sensitivity_reahced = [aflgo_sensitivity_df[reached_feature_name].notna().sum(), aflgoexp_sensitivity_df[reached_feature_name].notna().sum(), ffd_sensitivity_df[reached_feature_name].notna().sum()]
    sensitivity_triggered = [aflgo_sensitivity_df[triggered_feature_name].notna().sum(), aflgoexp_sensitivity_df[triggered_feature_name].notna().sum(), ffd_sensitivity_df[triggered_feature_name].notna().sum()]

    index = ['aflgo', 'aflgoexp', 'ffd']
    sensitivity_df_reached = pd.DataFrame({'original': original_reahced, 'sensitivity': sensitivity_reahced}, index=index)
    ax =  sensitivity_df_reached.plot.bar(rot=0)
    plt.savefig('../process_data_tosem/figures/sensitivity_num_of_bug_reached.png') 

    sensitivity_df_triggered = pd.DataFrame({'original': original_triggered, 'sensitivity': sensitivity_triggered}, index=index)
    ax = sensitivity_df_triggered.plot.bar(rot=0)
    output_path = os.path.join(output_dir, output_file_name)
    plt.savefig(output_path) 


def plot_bug_for_all_fuzzers(results, output_dir):
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
    output_path = os.path.join(output_dir, 'num_of_bug_reached_all_fuzzers.png')
    plt.savefig(output_path, format="png", dpi=300)

    plt.clf()

    plt.figure(figsize=(8, 6))
    plt.bar(x=fuzzer_lst, height=triggered_mean, yerr=triggered_stdev)
    plt.xlabel('Fuzzer')
    plt.ylabel('Number of Bugs Triggered')
    output_path = os.path.join(output_dir, 'num_of_bug_triggered_all_fuzzers.png')
    plt.savefig(output_path, format="png", dpi=300)


def get_instrumentation_time_for_all_fuzzers(fuzzers):
    instrumentation_time_results = dict.fromkeys(fuzzers, {})

    for fuzzer in fuzzers:
        bug_rt_file_path = f'../process_data_tosem/bug_analysis/{fuzzer}_survival_analysis'
        instrumentation_time_file_path = f'../process_data_tosem/build_time/{fuzzer}_build_time'

        bug_rt_df = pd.read_csv(bug_rt_file_path)
        instrumentation_time_df = pd.read_csv(instrumentation_time_file_path)

        instrumentation_time_df['time'] = instrumentation_time_df['time'].apply(lambda x: x.strip('s')).astype(float)
        rt_benchmarks = bug_rt_df['target'].values

        for benchmark in rt_benchmarks:
            instrumentation_time = instrumentation_time_df.loc[instrumentation_time_df['benchmark'] == benchmark, 'time'].iloc[0]
            instrumentation_time_results[fuzzer][benchmark] = instrumentation_time

    return instrumentation_time_results


if __name__ == '__main__':
    bug_result_output_dir = '../process_data_tosem/figures'
    bug_result_json_name = 'num_of_bug_rt.json'
    # merge_bug_results(bug_result_output_dir, bug_result_json_name)

    # read the bug results and plot the heatmap
    bug_result_file_name = os.path.join(bug_result_output_dir, bug_result_json_name)
    with open(bug_result_file_name, 'r') as json_file:
        num_bug_results = json.load(json_file)
    print(num_bug_results)

    fuzzers = ['afl', 'aflplusplus', 'libfuzzer', 'aflgo', 'aflgoexp', 'ffd', 'tunefuzz']

    # p_matrix_reached = get_p_val_for_num_bug(num_bug_results, fuzzers, 'reached', 'two-sided', True)
    # p_matrix_triggered = get_p_val_for_num_bug(num_bug_results, fuzzers, 'triggered', 'two-sided', True)

    # # plot the heatmaps for the number of bugs reached and triggered
    # p_val_heatmap_for_num_bug(p_matrix_reached, 'P Values for the Number of Bugs Reached', '../process_data_tosem/figures/num_bug_r_two_sided.png', fuzzers)
    # p_val_heatmap_for_num_bug(p_matrix_triggered, 'P Values for the Number of Bugs Triggered', '../process_data_tosem/figures/num_bug_t_two_sided.png', fuzzers)

    # # print out the latex tables
    # format_num_bug_and_survival_time_tables('../process_data_tosem/bug_analysis', fuzzers)

    # # process sensitivity experiments
    # plot_sensitivity_results('../process_data_tosem/figures', 'sensitivity_num_of_bug_triggered.png')

    # plot_bug_for_all_fuzzers(num_bug_results, '../process_data_tosem/figures')

    instrumentation_time_results = get_instrumentation_time_for_all_fuzzers(fuzzers)
    print(instrumentation_time_results)

    
    fuzzers = ['afl', 'aflplusplus', 'libfuzzer', 'aflgo', 'aflgoexp', 'ffd', 'tunefuzz']
    after_instrumentation_results = {}

    for fuzzer in fuzzers:
        bug_result_file_path = f'../process_data_tosem/bug_analysis/{fuzzer}_results.json'
        after_instrumentation_results[fuzzer] = results_after_counting_instrumentation_time(fuzzer, bug_result_file_path, instrumentation_time_results)
    print(after_instrumentation_results)

