import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt


def concat_build_time_df(dir_path):
    afl_build_time_df = pd.read_csv(os.path.join(dir_path, 'afl_build_time'))
    afl_build_time_df['afl'] = afl_build_time_df['time'].str.rstrip('s').astype(float)
    afl_build_time_df = afl_build_time_df.drop(columns=['file_name', 'time'])
    build_time_df = afl_build_time_df

    build_time_results = {}

    for file in os.listdir(dir_path):
        fuzzer_name = file.split('_')[0]
        df = pd.read_csv(os.path.join(dir_path, file))
        df[fuzzer_name] = df['time'].str.rstrip('s').astype(float)
        build_time_results[fuzzer_name] = df[fuzzer_name]

    for fuzzer in ['aflplusplus', 'libfuzzer', 'aflgo', 'ffd', 'tunefuzz']:
        build_time_df[fuzzer] = build_time_results[fuzzer]

    return build_time_df


def plot_instrumentation_time(df, fuzzers, output_dir):
    x = df['benchmark']
    y_values = df.set_index('benchmark')  

    plt.figure(figsize=(10, 12))
    markers = ['o', '*', '^', '+', 's', 'D']
    columns = fuzzers
    for i in range(len(fuzzers)):
        plt.scatter(range(len(df)), df[columns[i]], label=columns[i])  
        plt.plot(range(len(df)), df[columns[i]], linestyle='-', marker=markers[i], markersize=3)

    categories = df['benchmark']
    print(columns)
    category_to_num = {cat: i for i, cat in enumerate(categories)}  
    x_values = df['benchmark'].map(category_to_num) 
    plt.xticks(ticks=range(len(categories)), labels=categories)
    plt.xticks(rotation=90) 
    plt.title("Instrumentation Time for each Benchmark")
    plt.xlabel("Benchmark")
    plt.ylabel("Time (s)")
    plt.legend()
    plt.grid(True)
    output_path = os.path.join(output_dir, 'instrumentation_time.png')
    plt.savefig(output_path, format="png", dpi=300)


if __name__ == '__main__':
    # we do not include aflgoexp because aflgoexp is the same as aflgo except for the options used for fuzzing
    fuzzers = ['afl', 'aflplusplus', 'libfuzzer', 'aflgo', 'ffd', 'tunefuzz']
    build_time_df = concat_build_time_df('../process_data_tosem/build_time')
    plot_instrumentation_time(build_time_df, fuzzers, '../process_data_tosem/figures')
