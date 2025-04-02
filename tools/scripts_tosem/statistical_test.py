from scipy.stats import mannwhitneyu, rankdata
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import json
import os


def mann_whitney_u_test(sample1, sample2, alternative):
    U1, p = mannwhitneyu(sample1, sample2, alternative=alternative, method='auto')
    return p


# adapted from survival_analysis.py
def get_time_to_bug(file_path, results, fuzzer_name=None) -> dict:
    with open(file_path, 'r') as file:
        data = json.load(file).get('results', {})
    for fuzzer, f_data in data.items():
        for target, t_data in f_data.items():
            for program, p_data in t_data.items():
                for run, r_data in p_data.items():
                    for metric, m_data in r_data.items():
                        # print(metric)
                        # print(m_data)
                        if fuzzer_name:
                            results[fuzzer_name][metric][int(run)] += len(m_data)
                        else:
                            results[fuzzer][metric][int(run)] += len(m_data)
    return results


def results_after_counting_instrumentation_time(fuzzer, file_path, instrumentation_results, fuzzer_name=None) -> dict:
    num_trial = 10
    results = {'reached': [0]*num_trial, 'triggered': [0]*num_trial}
    with open(file_path, 'r') as file:
        data = json.load(file).get('results', {})
    for fuzzer, f_data in data.items():
        for target, t_data in f_data.items():
            for program, p_data in t_data.items():
                for run, r_data in p_data.items():
                    for metric, m_data in r_data.items():
                        instrumentation_time = instrumentation_results[fuzzer][target]
                        time_to_bug_lst = list(m_data.values())
                        if len(time_to_bug_lst) > 0:
                            time_to_bug = list(m_data.values())[0]
                            total_time = time_to_bug + instrumentation_time
                            if total_time <= 600:
                                results[metric][int(run)] += len(m_data)
                            else:
                                print(fuzzer, target, program, run, metric, time_to_bug, instrumentation_time, total_time)
    return results


def get_p_val_for_num_bug(result_dict: dict, fuzzers, metric, alternative, verbose=False):
    num_of_fuzzers = len(fuzzers)
    p_matrix = [[np.nan for _ in range(num_of_fuzzers)] for _ in range(num_of_fuzzers)]
    for i in range(num_of_fuzzers):
        for j in range(num_of_fuzzers):
            if j <= i:
                pass
            else:
                p = mann_whitney_u_test(result_dict[fuzzers[i]][metric], result_dict[fuzzers[j]][metric], alternative)
                p_matrix[i][j] = p
                # if alternative == 'two-sided':
                #     p_matrix[j][i] = p
                if verbose:
                    print(f'{fuzzers[i]}, {fuzzers[j]}, {p}')
                    print(result_dict[fuzzers[i]][metric], result_dict[fuzzers[j]][metric])
    if verbose:
        for row in p_matrix:
            print(row)
    return p_matrix


def p_val_heatmap_for_num_bug(matrix, fuzzers, file_name):
    plt.figure(figsize=(10, 8))  
    mask = np.isnan(matrix)
    ax = sns.heatmap(matrix, cmap='viridis_r', mask=mask, annot=True, fmt=".6f")
    ax.set_xticklabels(fuzzers)
    ax.set_yticklabels(fuzzers)
    plt.xticks(rotation=30)
    plt.yticks(rotation=30)
    # plt.title(fig_title, fontsize=20)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    # save the plot locally
    plt.savefig(file_name, format="png", dpi=300)


# given n samples of data, each sample consists of several data points
# use mann whitney u tests to decide which sample has greater distribution 
def test_greater_distribution(samples, threshold=0.05):
    p_val_counts = [0] * len(samples)
    for i in range(len(samples)):
        for j in range(len(samples)):
            if i != j:
                u1, p = mannwhitneyu(samples[i], samples[j], alternative='greater')
                if p < threshold:
                    p_val_counts[i] += 1 
    max_index = np.argmax(p_val_counts)
    return max_index

