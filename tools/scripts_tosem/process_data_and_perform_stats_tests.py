from pathlib import Path
import pandas as pd
import numpy as np
import glob
import os
from statistical_test import *


def process_last_update_log(log_path, output_path):

    os.makedirs(output_path, exist_ok=True)

    if 'tunefuzz' in log_path:
        start_index = -4
        plot_data_pattern = '*/*/*/*/*/findings/default/plot_data'
    elif 'aflpp' in log_path or 'aflplusplus' in log_path:
        start_index = -4
        plot_data_pattern = '*/*/*/*/*/findings/default/plot_data'
        time_col_name = '# relative_time'
    else:
        start_index = -3
        plot_data_pattern = '*/*/*/*/*/findings/plot_data'
        time_col_name = '# unix_time'

    plot_data_files = list(Path(log_path).glob(plot_data_pattern))

    for plot_data in plot_data_files:
        print(plot_data)
        df = pd.read_csv(plot_data)
        if len(df) > 0:
            if 'tunefuzz' in log_path:
                last_update = df.index.values[-1]
            else:
                last_update = df[time_col_name].values[-1]
        else:
            last_update = -1
        

        print(plot_data)

        plot_data_str = str(plot_data).split('/')
        iteration = plot_data_str[start_index]
        program = plot_data_str[start_index-1]
        target = plot_data_str[start_index-2]
        fuzzer = plot_data_str[start_index-3]

        print(iteration, program, target, fuzzer, last_update)

        output_file_name = f'{fuzzer}_{target}_{program}_last_update'
        output_file_path = os.path.join(output_path, output_file_name)
        if not os.path.exists(output_file_path):
            with open(output_file_path, 'w') as file:
                file.write('fuzzer,target,program,iteration,last_update\n')

        #fuzzer,target,program,iteration
        output = f'{fuzzer},{target},{program},{iteration},{last_update}\n'
        with open(output_file_path, 'a') as file:
            file.write(output)


def merge_execs_done_and_new_fuzzing_time(benchmarks, fuzzers, last_update_path, simple_fuzzer_stats_path, output_dir):
    for fuzzer in fuzzers:
        for benchmark in benchmarks:
            last_update_file = f'{fuzzer}_{benchmark}*_last_update'
            simple_fuzzer_stats_file = f'{fuzzer}_{benchmark}*_simple_fuzzer_stats'

            last_update_files = list(Path(os.path.join(last_update_path, fuzzer)).glob(last_update_file))
            simple_fuzzer_stats_files = list(Path(os.path.join(simple_fuzzer_stats_path, fuzzer)).glob(simple_fuzzer_stats_file))

            if len(last_update_files) > 0 and len(simple_fuzzer_stats_files) > 0:
                last_update_df = pd.read_csv(last_update_files[0])
                simple_fuzzer_stats_df = pd.read_csv(simple_fuzzer_stats_files[0])

                simple_fuzzer_stats_df.drop(columns=['fuzzer', 'target', 'program'], inplace=True)
                merged_stats_df = pd.merge(last_update_df, simple_fuzzer_stats_df, on='iteration', how='inner')
                
                if fuzzer == 'tunefuzz' or fuzzer == 'aflplusplus':
                    merged_stats_df['fuzzing_time'] = merged_stats_df['last_update']
                else:
                    merged_stats_df['fuzzing_time'] = np.where((merged_stats_df['last_update'] == -1) | (merged_stats_df['last_update'] == 0), 0, merged_stats_df['last_update'] - merged_stats_df['start_time'])
                merged_stats_df.drop(columns=['last_update', 'start_time'], inplace=True)
                print(merged_stats_df)


                output_path = os.path.join(output_dir, fuzzer)
                os.makedirs(output_path, exist_ok=True)

                file_prefix = str(last_update_files[0]).split('/')[-1].replace('_last_update', '')
                output_file_name = f'{file_prefix}_final_fuzzer_stats'
                output_file_path = os.path.join(output_path, output_file_name)

                print(merged_stats_df)
                print(output_file_path)
                merged_stats_df.to_csv(output_file_path, index=False)  


def perform_stats_test_and_format_table(fuzzers, benchmarks, log_path, feature_name):
    for benchmark in benchmarks:
        result = {}
        for fuzzer in fuzzers:
            file_path = os.path.join(log_path, fuzzer)
            file_prefix = f'{fuzzer}_{benchmark}'
            # find the first matching file
            full_file_path = next(glob.iglob(f'{file_path}/{file_prefix}*'))
            df = pd.read_csv(full_file_path)
            if feature_name == 'Cover.2':
                df[feature_name] = df[feature_name].str.rstrip('%').astype(float)
            result[fuzzer] = df[feature_name].values
        result_values = list(result.values())
        max_index = test_greater_distribution(result_values)

        # formatting
        benchmark = benchmark.replace('_', '\_')
        mean_result = [round(np.mean(x),2) for x in result_values]
        mean_result_string = list(map(str, mean_result))
        # highlight the value with statistical significance in gray
        mean_result_string[max_index] = '\colorbox{gray!40} {' + mean_result_string[max_index] + '}'
        formatted_result = benchmark + ' & ' + ' & '.join(mean_result_string) + ' \\\\'
        print(formatted_result)


if __name__ == '__main__':

    benchmarks = ['libpng_4_1', 'libsndfile_2_1', 'libsndfile_7_1', 'libsndfile_15_1', 'libtiff_6_1', 'libtiff_7_1', 'libtiff_9_1', 'libtiff_10_1', 'libxml2_1_2', 'libxml2_2_1', 'libxml2_8_1', 'libxml2_10_2', 'libxml2_12_2', 'libxml2_14_1', 'libxml2_15_1', 'libxml2_16_1', 'libxml2_16_2', 'openssl_1_3', 'openssl_1_5', 'openssl_4_4', 'openssl_5_1', 'openssl_6_4', 'openssl_6_5', 'openssl_6_6', 'openssl_7_2', 'openssl_7_4', 'openssl_8_1', 'openssl_9_1', 'openssl_10_5', 'openssl_11_4', 'openssl_11_6', 'openssl_12_6', 'openssl_13_2', 'openssl_16_6', 'openssl_17_2', 'openssl_17_4', 'openssl_18_5', 'openssl_19_1', 'openssl_20_3', 'openssl_20_4', 'php_4_1', 'php_6_2', 'php_11_2', 'php_15_2', 'php_16_3', 'poppler_3_1', 'poppler_9_1', 'poppler_17_1', 'sqlite3_18_1', 'sqlite3_20_1']
    fuzzers = ['afl', 'aflgo', 'aflgoexp', 'aflplusplus', 'ffd', 'tunefuzz']


    # # process the tables for the feature last_update
    # for fuzzer in fuzzers:
    #     log_path=f'/Volumes/GitRepo/data/{fuzzer}'
    #     output_path = '../process_data_tosem/last_update'
    #     output_path = os.path.join(output_path, fuzzer)
    #     process_last_update_log(log_path, output_path)


    # # merge the tables to be the final_fuzzer_stats tables
    # last_update_path = '../process_data_tosem/last_update'
    # simple_fuzzer_stats_path = '../process_data_tosem/simple_fuzzer_stats'
    # merge_execs_done_and_new_fuzzing_time(benchmarks, fuzzers, last_update_path, simple_fuzzer_stats_path, '../process_data_tosem/final_fuzzer_stats')
    

    # # sanity check for any missing benchmarks
    # for fuzzer in fuzzers:
    #     log_path = f'../process_data_tosem/final_fuzzer_stats/{fuzzer}'
    #     for benchmark in benchmarks:
    #         pattern = f'*{benchmark}*'
    #         searched_files = list(Path(log_path).glob(pattern))
    #         if len(searched_files) != 1:
    #             print(benchmark)
    #             print(searched_files)


    # stats tests for mean execution counts, mean fuzzing time, and mean total coverage
    fuzzer_stats_log_path = '../process_data_tosem/final_fuzzer_stats/'
    print('The table for the actual fuzzing time')
    perform_stats_test_and_format_table(fuzzers, benchmarks, fuzzer_stats_log_path, 'fuzzing_time')
    print('The table for the number of executions done')
    perform_stats_test_and_format_table(fuzzers, benchmarks, fuzzer_stats_log_path, 'execs_done')


    fuzzer_naming_convention2 = ['afl', 'aflpp', 'libfuzzer', 'aflgo', 'aflgoexp', 'ffd', 'tunefuzz']
    log_path = '../process_data_tosem/coverage/total_coverage/'
    # branch coverage in percentage
    feature_name = 'Cover.2'
    print('The table for coverage')
    perform_stats_test_and_format_table(fuzzer_naming_convention2, benchmarks, log_path, feature_name)
