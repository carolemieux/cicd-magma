import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics
from statistical_test import *


def plot_bug_count_comparison(data, data_to_compare, output_path):
    categories = list(data['reached'].keys())
    num_categories = len(categories)

    bar_width = 0.2
    index = np.arange(num_categories)

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 6), sharey=True)

    for i, metric in enumerate(['reached', 'triggered']):

        original_data = data[metric]
        sensitivity_data = data_to_compare[metric]

        original_mean = [statistics.mean(val) for val in original_data.values()]
        sensitivity_mean = [statistics.mean(val) for val in sensitivity_data.values()]
        original_stdev = [statistics.stdev(val) for val in original_data.values()]
        sensitivity_stdev = [statistics.stdev(val) for val in sensitivity_data.values()]
        
        original_bar_container = axes[i].bar(index + 0 * bar_width, original_mean, bar_width, yerr=original_stdev, label='original')
        sensitivity_bar_container = axes[i].bar(index + 1 * bar_width, sensitivity_mean, bar_width, yerr=sensitivity_stdev, label='sensitivity')

        axes[i].bar_label(original_bar_container, fmt='{:,.0f}')
        axes[i].bar_label(sensitivity_bar_container, fmt='{:,.0f}')

    axes[0].set_xlabel('Fuzzers')
    axes[0].set_ylabel('Number of Bugs Reached')
    axes[0].set_xticks(index + bar_width * 1/2)
    axes[0].set_xticklabels(categories)

    axes[1].set_xlabel('Fuzzers')
    axes[1].set_ylabel('Number of Bugs Triggered')
    axes[1].set_xticks(index + bar_width * 1/2)
    axes[1].set_xticklabels(categories)

    # Show legend
    handles, labels = plt.gca().get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncols=2)

    plt.savefig(output_path) 


# helper function to swap the outer and inner keys of a json object
def swap_json_keys(data):
    swapped_json = {}
    for outer_key, inner_dict in data.items():
        for inner_key, value in inner_dict.items():
            # prevent access error
            if inner_key not in swapped_json:
                swapped_json[inner_key] = {}
            swapped_json[inner_key][outer_key] = value
    return swapped_json


if __name__ == '__main__':

    # original_file_path = '../process_data_tosem/original_experiments/figures/num_of_bugs_w_instrumentation.json'
    # sensitivity_file_path = '../process_data_tosem/sensitivity_experiments/figures/num_of_bugs_w_instrumentation.json'

    original_file_path = '../process_data_tosem/original_experiments/figures/num_of_bugs_wo_instrumentation.json'
    sensitivity_file_path = '../process_data_tosem/sensitivity_experiments/figures/num_of_bugs_wo_instrumentation.json'

    with open(original_file_path, 'r') as json_file:
        original_num_of_bug_result = json.load(json_file)
        original_num_of_bug_result.pop('afl')
        original_num_of_bug_result.pop('aflplusplus')
        original_num_of_bug_result.pop('libfuzzer')
        original_num_of_bug_result.pop('tunefuzz')

    with open(sensitivity_file_path, 'r') as json_file:
        sensitivity_num_of_bug_result = json.load(json_file)
    
    # stats tests
    sensitivity_fuzzers = ['aflgo', 'aflgoexp', 'ffd']
    for fuzzer in sensitivity_fuzzers:
        for metric in ['reached', 'triggered']:
            original_sample = original_num_of_bug_result[fuzzer][metric]
            sensitivity_sample = sensitivity_num_of_bug_result[fuzzer][metric]
            u1, p = mannwhitneyu(original_sample, sensitivity_sample, alternative='greater')
            if p < 0.05:
                print('Greater')
            else:
                print(f'Non-significant: {fuzzer}, {metric}, {original_sample}, {sensitivity_sample}')
        
    original_result = swap_json_keys(original_num_of_bug_result)
    sensitivity_result = swap_json_keys(sensitivity_num_of_bug_result)
    print(original_result)
    print(sensitivity_result)

    # plot_bug_count_comparison(original_result, sensitivity_result, '../process_data_tosem/original_vs_sensitivity_figures/original_vs_sensitivity_bug_count.png')
    plot_bug_count_comparison(original_result, sensitivity_result, '../process_data_tosem/original_vs_sensitivity_figures/original_vs_sensitivity_bug_count_wo_instrumentation.png')
