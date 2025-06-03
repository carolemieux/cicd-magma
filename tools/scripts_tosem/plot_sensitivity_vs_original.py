import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statistical_test import *


def plot_bug_count_comparison(data, data_to_compare, output_path):
    categories = list(data['original'].keys())
    num_groups = len(data)
    num_categories = len(categories)

    bar_width = 0.2
    index = np.arange(num_categories)

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 6), sharey=True)

    group_positions = np.arange(num_groups)

    ax = axes[0]
    for i, (group_name, values) in enumerate(data.items()):
        positions = index + group_positions[i] * bar_width
        bar_container = ax.bar(positions, list(values.values()), bar_width, label=group_name)
        ax.bar_label(bar_container, fmt='{:,.0f}')

    ax.set_xlabel('Fuzzers')
    ax.set_ylabel('Number of Bugs Reached')
    ax.set_xticks(index + bar_width * (num_groups - 1) / 2)
    ax.set_xticklabels(categories)

    ax = axes[1]
    for i, (group_name, values) in enumerate(data_to_compare.items()):
        positions = index + group_positions[i] * bar_width
        bar_container = ax.bar(positions, list(values.values()), bar_width, label=group_name)
        ax.bar_label(bar_container, fmt='{:,.0f}')

    ax.set_xlabel('Fuzzers')
    ax.set_ylabel('Number of Bugs Triggered')
    ax.set_xticks(index + bar_width * (num_groups - 1) / 2)
    ax.set_xticklabels(categories)

    # Show legend
    handles, labels = plt.gca().get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncols=2)
    plt.savefig(output_path) 


if __name__ == '__main__':
    # aflgo r-15 t-6 aflgoexp r-12 t-4 ffd r-12 t-5
    # aflgo r-15 t-6 aflgoexp r-14 t-5 ffd r-14 t-5

    reached_dict = {
        'original': {'aflgo': 15, 'aflgoexp': 14, 'ffd': 14},
        'sensitivity': {'aflgo': 15, 'aflgoexp': 12, 'ffd': 12},
    }
    triggered_dict = {
        'original': {'aflgo': 6, 'aflgoexp': 5, 'ffd': 5},
        'sensitivity': {'aflgo': 6, 'aflgoexp': 4, 'ffd': 5},
    }

    plot_bug_count_comparison(reached_dict, triggered_dict, '../process_data_tosem/original_vs_sensitivity_figures/reached_bug_count_comparison.png')


    original_file_path = '../process_data_tosem/original_experiments/figures/num_of_bugs_w_instrumentation.json'
    sensitivity_file_path = '../process_data_tosem/sensitivity_experiments/figures/num_of_bugs_w_instrumentation.json'

    with open(original_file_path, 'r') as json_file:
        original_num_of_bug_result = json.load(json_file)

    with open(sensitivity_file_path, 'r') as json_file:
        sensitivity_num_of_bug_result = json.load(json_file)

    sensitivity_fuzzers = ['aflgo', 'aflgoexp', 'ffd']

    for fuzzer in sensitivity_fuzzers:
        for metric in ['reached', 'triggered']:
            original_sample = original_num_of_bug_result[fuzzer][metric]
            sensitivity_sample = sensitivity_num_of_bug_result[fuzzer][metric]
            u1, p = mannwhitneyu(original_sample, sensitivity_sample, alternative='greater')

            print(fuzzer, metric)
            print(original_sample)
            print(sensitivity_sample)

            if p < 0.05:
                print('Greater\n')
            else:
                print('Non-significant\n')
        