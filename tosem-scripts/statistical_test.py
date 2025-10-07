from scipy.stats import mannwhitneyu
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json


def mann_whitney_u_test(sample1, sample2, alternative):
    U1, p = mannwhitneyu(sample1, sample2, alternative=alternative, method='auto')
    return p


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


def p_val_heatmap_for_num_bug_compact(matrix1, matrix2, fuzzers, file_name):

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(18, 7))
    
    sns.heatmap(matrix1, ax=axes[0], cmap='viridis_r', mask=np.isnan(matrix1), annot=True, fmt=".6f")
    sns.heatmap(matrix2, ax=axes[1], cmap='viridis_r', mask=np.isnan(matrix2), annot=True, fmt=".6f")

    axes[0].set_xticklabels(fuzzers)
    axes[0].set_yticklabels(fuzzers)
    axes[0].set_title('Number of Bugs Reached')

    axes[1].set_xticklabels(fuzzers)
    axes[1].set_yticklabels(fuzzers)
    axes[1].set_title('Number of Bugs Triggered')

    # save the plot locally
    fig.tight_layout()
    plt.savefig(file_name, format="png", dpi=300)


# adapted from survival_analysis.py
def get_time_to_bug(file_path, results) -> dict:
    with open(file_path, 'r') as file:
        data = json.load(file).get('results', {})
    for fuzzer, f_data in data.items():
        for target, t_data in f_data.items():
            for program, p_data in t_data.items():
                for run, r_data in p_data.items():
                    for metric, m_data in r_data.items():
                        results[fuzzer][metric][int(run)] += len(m_data)


def get_time_to_bug_with_instrumentation_time(file_path, results, instrumentation_results) -> dict:
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
                                results[fuzzer][metric][int(run)] += len(m_data)
                            else:
                                print(fuzzer, target, program, run, metric, time_to_bug, instrumentation_time, total_time)


# given n samples of data, each sample consists of several data points
# use mann whitney u tests to decide which sample has greater distribution 
def test_greater_distribution(samples, threshold=0.05):
    assert len(samples) > 0 
    p_val_counts = [0] * len(samples)
    for i in range(len(samples)):
        for j in range(len(samples)):
            if i != j:
                u1, p = mannwhitneyu(samples[i], samples[j], alternative='greater')
                if p < threshold:
                    p_val_counts[i] += 1 
    max_index = np.argmax(p_val_counts)
    max_val = p_val_counts[max_index]
    max_counts = p_val_counts.count(max_val)
    # print(p_val_counts)
    if max_counts > 1:
        return -1
    else:
        return max_index
    

# outdated as we'd like a more compact version as in p_val_heatmap_for_num_bug_compact
# p_val_heatmap_for_num_bug(p_matrix_reached, fuzzers, '../process_data_tosem/original_experiments/figures/num_bug_r_wo_instrumentation_time_two_sided.png')
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
