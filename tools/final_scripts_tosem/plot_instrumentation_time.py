import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt


BASE_RESULTS_DIR= "../main-results"

fuzzers = ['afl', 'aflplusplus', 'libfuzzer',  'aflgoexp', 'aflgo', 'ffd', 'windranger', 'tunefuzz']
legend_items = ['AFL', 'AFL++', 'libFuzzer', 'AFLGoE', 'AFLGo', 'FFD', 'WindRanger', 'TuneFuzz']

def concat_build_time_df():
    afl_build_time_df = pd.read_csv(os.path.join(BASE_RESULTS_DIR, 'afl-inst.csv'), header=None)
    afl_build_time_df['afl'] = afl_build_time_df[1].astype(float)
    afl_build_time_df = afl_build_time_df.drop(columns=[1])
    build_time_df = afl_build_time_df

    for fuzzer in fuzzers[1:]:
        instrumentation_file_name = f'{fuzzer}-inst.csv'
        df = pd.read_csv(os.path.join(BASE_RESULTS_DIR, instrumentation_file_name), header=None)
        #build_time_df[fuzzer] =  df[1]
        build_time_df.insert(len(build_time_df.columns), fuzzer, df[1])

    build_time_df.set_index(0, inplace=True)


    return build_time_df


def plot_instrumentation_time(df, output_dir):
    x = list(df.index)
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

    plt.figure(figsize=(10, 7))
    markers = ['o', '*', '^', 'X','+', 's', 'D', 'x']
    columns = fuzzers
    for i in range(len(fuzzers)):
        #plt.scatter(range(len(df)), df[columns[i]], label=columns[i])
        plt.plot(range(len(df)), df[columns[i]], linestyle='-', marker=markers[i], markersize=5, label=legend_items[i], color=okabe_ito[i])

    plt.xticks(ticks=range(len(x)), labels=x)
    plt.xticks(rotation=90,size=8)
    #plt.title("Instrumentation Time for each Benchmark")
    plt.xlabel("Benchmark")
    plt.ylabel("Instrumentation Time (s)")
    # magic from https://stackoverflow.com/questions/22263807/how-is-order-of-items-in-matplotlib-legend-determined
    handles, labels = plt.gca().get_legend_handles_labels()
    order = [0,1,2,4,3,5,6,7]
    plt.legend([handles[idx] for idx in order],[labels[idx] for idx in order])
    plt.grid(True)
    output_path = os.path.join(output_dir, 'instrumentation_time.pdf')
    plt.tight_layout()
    plt.savefig(output_path)


if __name__ == '__main__':
    build_time_df = concat_build_time_df()
    plot_instrumentation_time(build_time_df, 'figures')
