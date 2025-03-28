import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pickle


def traverse_file_path(file_path):
    dir_count = 0
    file_count = 0
    total_size = 0
    for root_dir, sub_dirs, files in os.walk(file_path, topdown=False):
        if '.DS_Store' in files:
            files.remove('.DS_Store')
        for file in files:
            full_path = os.path.join(root_dir, file)
            size = os.path.getsize(full_path) / 1000000
            total_size += size
        dir_count += len(sub_dirs)
        file_count += len(files)
    print(f'File path: {file_path}\nDir count: {dir_count} \t File count: {file_count} \t File size: {total_size} MB')
    return dir_count, file_count, total_size


def traverse_fuzzer_data(fuzzer_data_path):
    result_dict = {
        'file_path': [],
        'dir_count': [],
        'file_count': [],
        'dir_size': []
    }
    dirs = os.listdir(fuzzer_data_path)
    if '.DS_Store' in dirs:
        dirs.remove('.DS_Store')
    for dir in dirs:
        dir_path = os.path.join(fuzzer_data_path, dir)
        dir_count, file_count, total_size = traverse_file_path(dir_path)
        result_dict['file_path'].append(dir_path)
        result_dict['dir_count'].append(dir_count)
        result_dict['file_count'].append(file_count)
        result_dict['dir_size'].append(total_size)
    return pd.DataFrame(result_dict)


def process_raw_file_dfs(dfs, feature_name):
    # data preprocessing
    processed_dfs = {}
    for fuzzer, df in dfs.items():
        df['file_path'] = df['file_path'].apply(lambda x: os.path.basename(x))
        df = df.set_index('file_path')
        processed_dfs[fuzzer] = df

    # sort before plotting
    base_df = processed_dfs['aflplusplus']
    base_df_sorted = base_df.sort_values(by=feature_name)
    sorted_benchmark_index = base_df_sorted.index

    sorted_dfs = {}
    for fuzzer, df in processed_dfs.items():
        sorted_dfs[fuzzer] = df.loc[sorted_benchmark_index]
    return sorted_dfs, sorted_benchmark_index


def plot_file_data(sorted_dfs, sorted_benchmark_index, fuzzers, feature_name, output_dir, feature_title):
    # plot
    plt.figure(figsize=(16, 14))
    markers = ['o', '*', '^', '+', 's', 'D', 'P']
    columns = fuzzers

    for i in range(len(fuzzers)):
        fuzzer = fuzzers[i]
        df = sorted_dfs[fuzzer]
        plt.scatter(range(len(df)), df[feature_name], label=fuzzer)
        plt.plot(range(len(df)), df[feature_name], linestyle='-', linewidth=1.0, marker=markers[i], markersize=2)
    
    categories = sorted_benchmark_index
    category_to_num = {cat: i for i, cat in enumerate(categories)}  
    x_values = sorted_benchmark_index.map(category_to_num) 

    plt.xticks(ticks=range(len(categories)), labels=categories, fontsize=15)
    plt.xticks(rotation=90) 
    plt.yticks(fontsize=15)

    plt.title(f'{feature_title} for Each Benchmark', fontsize=22, fontweight='bold')
    plt.xlabel("Benchmark", fontsize=22)
    plt.ylabel(feature_title, fontsize=22)
    plt.legend(fontsize=18)

    plt.grid(True)
    output_path = os.path.join(output_dir, f'{feature_title} for Each Benchmark.png')
    plt.savefig(output_path, format="png", dpi=300)


def box_plot_for_fuzzer_dfs(dfs, fuzzers, feature_name, feature_title, output_dir):
    combined_results = {}
    for fuzzer in fuzzers:
        df = dfs[fuzzer]
        combined_results[fuzzer] = df[feature_name]
    combined_df = pd.DataFrame(combined_results)
    print(combined_df)
    print(combined_df)
    plt.figure(figsize=(10, 6))
    combined_df.boxplot()
    plt.title(f'{feature_title} Box Plot', fontsize=22, fontweight='bold')
    plt.xlabel('Fuzzers', fontsize=18)
    plt.ylabel(f'{feature_title}', fontsize=18)
    plt.xticks(fontsize=14) 
    plt.yticks(fontsize=14)
    output_path = os.path.join(output_dir, f'{feature_title} Box Plot.png')
    plt.savefig(output_path, format="png", dpi=300)
    return combined_df



def bar_chart_for_all_fuzzer_comparison(combined_df, feature_title, output_dir):
    plt.figure(figsize=(10, 6))
    ax = combined_df.sum().sort_values(ascending=True).plot.bar(rot=0)
    plt.title(f'Total {feature_title} for Each Fuzzer', fontsize=22, fontweight='bold')
    plt.xlabel('Fuzzers', fontsize=18)
    plt.ylabel(f'{feature_title}', fontsize=18)
    plt.xticks(fontsize=14) 
    plt.yticks(fontsize=14)
    output_path = os.path.join(output_dir, f'Total {feature_title} Bar Chart.png')
    plt.savefig(output_path, format="png", dpi=300)


if __name__ == '__main__':
    fuzzers = ['afl', 'aflgo', 'aflgoexp', 'aflplusplus', 'ffd', 'libfuzzer', 'tunefuzz']
    # result_dfs = {}
    # for fuzzer in fuzzers:    
    #     fuzzer_data_path = f'/Volumes/GitRepo/fuzzing-data/data/{fuzzer}/ar/{fuzzer}'
    #     result_df = traverse_fuzzer_data(fuzzer_data_path)
    #     result_dfs[fuzzer] = result_df
    # with open('file_analysis.pickle', 'wb') as f:
    #     pickle.dump(result_dfs, f)

    with open('file_analysis.pickle', 'rb') as f:
        result_dfs = pickle.load(f)
        dir_size_sorted_dfs, sorted_index1 = process_raw_file_dfs(result_dfs, 'dir_size')
        plot_file_data(dir_size_sorted_dfs, sorted_index1, fuzzers, 'dir_size', '.', 'Data Size (MB)')

        file_count_sorted_dfs, sorted_index2 = process_raw_file_dfs(result_dfs, 'file_count')
        plot_file_data(file_count_sorted_dfs, sorted_index2, fuzzers, 'file_count', '.', 'Number of Files')
        
        dir_size_combined_df = box_plot_for_fuzzer_dfs(dir_size_sorted_dfs, fuzzers, 'dir_size', 'Data Size (MB)', '.')
        file_count_combined_df = box_plot_for_fuzzer_dfs(file_count_sorted_dfs, fuzzers, 'file_count', 'Number of Files', '.')

        dir_size_combined_df = dir_size_combined_df/1000
        bar_chart_for_all_fuzzer_comparison(dir_size_combined_df, 'Data Size (GB)', '.')
        bar_chart_for_all_fuzzer_comparison(file_count_combined_df, 'Number of Files (Million)', '.')

