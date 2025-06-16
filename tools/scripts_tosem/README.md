# Steps to produce process data and corresponding latex tables
Suppose we have a directory named `data` where the fuzzing data for each fuzzer is stored in its individual directory. For example, the fuzzing data for tunefuzz is stored in `data/tunefuzz`.

## Data preprocessing
**TuneFuzz**
* For the openssl_16_6 benchmark, we need to rename the folders in the `ar` folder because the iterations are named as "0, 1, 2, 3, 4, 5, 7, 8, 9, 10" without the 6th iteration. This will lead to `IndexError: list assignment index out of range` when executing the `survival_analysis.py` file in `ContinuousFuzzBench/tools/benchd`. We need to rename the corresponding log files in the folder `data/tunefuzz/log` to have the correct iteration order.

**AFLGoExp**
* Need to rename the first subdirectory of `data/aflgoexp/ar` from `aflgo` to `aflgoexp`.
* Need to rename all prefixes from `aflgo` to `aflgoexp` for the `*.log` files in the `data/aflgoexp/log` directory. Go to the directory `ContinuousFuzzBench/tools/scripts_tosem` and execute the `utility.py` to rename the files.
* The thesis experiments include the fuzzing data for afl, afl++, aflgo, aflgoexp, ffd, and libfuzzer. However, for aflgoexp, the log for the benchmark libpng_4_1 is cached so that Docker does not record its instrumentation time. We repeat the experiments for the benchmark libpng_4_1 with aflgoexp in this complete evaluation for TOSEM submission and use this fuzzing data for evaluation. Note that the iterations need to be renamed to follow the correct iteration order.

**Sensitivity experiments**
* Need to reformat the data for sensitivity experiments to be in format of `data/[fuzzer_name]/ar/[fuzzer_name]/[benchmark_name]/[program_name]...`
* Need to rename the iteration directories for the benchmark poppler_9_1 for the fuzzer aflgo from "1 2 3 4 5 6 7 9 10" to "1 2 3 4 5 6 7 8 9".
* We do not include the process data for the number of bugs reached and triggered with instrumentation time because the build log for some benchmarks are cached, thus lacking the information of instrumentation time.
* We do not include the process data for fuzzer_stats and coverage values for sensitivity experiments at this time due to the different format of sensitivity log.

## Bug analysis
Go to the directory `ContinuousFuzzBench/tools/benchd` to generate the survival analysis results.

Run the file `exp2json.py` for each fuzzer, e.g.,
```
# make sure the output directory exists
mkdir ../process_data_tosem/original_experiments/bug_analysis
python3 exp2json.py --workers 32 -v [path_to_data/afl] [output_directory/afl_results.json]
```

Run the file `survival_analysis.py` to perform the survival analysis for each fuzzer, e.g.,
```
python3 survival_analysis.py -n 10 -t 600 [output_directory/afl_results.json] > [output_directory/afl_survival_analysis]
```

Extract and plot instrumentation time, e.g.,
```
./process_build_time.sh [path_to_data] [output_directory]
python3 plot_instrumentation_time.py
```

Run the scripts below to:
1. Process the number of bugs reached and triggered results with/without instrumentation time
2. Plot the heatmaps for the Mann-Whitney U test results for the number of bugs reached and triggered with/without instrumentation time
3. Get the instrumentation time for all benchmarks by fuzzers
4. Plot the mean number of bugs reached and triggered with/without instrumentation time
5. Format and print the latex tables for the mean survival time with/without instrumentation time
```
python3 process_bug_analysis.py 
```

## Fuzzer stats
Run the script `process_all_fuzzer_stats.sh` to process the raw `fuzzer_stats` files and extract the `start_time` and `execs_done` values for each fuzzer. E.g.,
```
./process_all_fuzzer_stats.sh "process_simple_fuzzer_stats.sh" "[path_to_data]" "../process_data_tosem/original_experiments/simple_fuzzer_stats"
```

## Coverage values
Process the raw coverage data for all fuzzers
```
# for original experiments
./process_all_fuzzer_total_coverage.sh "process_total_coverage.sh" "[path_to_coverage_data]" "../process_data_tosem/original_experiments/coverage/total_coverage"
./process_all_fuzzer_target_fn_coverage.sh "process_target_function_coverage.sh" "[path_to_coverage_data]" "../process_data_tosem/original_experiments/coverage/target_function_coverage"

# for sensitivity experiments
./process_total_coverage.sh [path_to_sensitivity_coverage] "../process_data_tosem/sensitivity_experiments/coverage/total_coverage"
./process_target_function_coverage.sh "target_functions.csv" [path_to_sensitivity_coverage] "../process_data_tosem/sensitivity_experiments/coverage/target_function_coverage"
```

## Pair-wise Mann-Whitney U tests
Perform pair-wise Mann-Whitney U tests and print the formatted latex tables for mean total coverage, mean execution counts, and mean actual fuzzing time.
```
python3 process_data_and_perform_stats_tests.py
```

## Checksum results
```
./compare_checksum.sh [path_to_checksum_before_inserting_patches] [path_to_checksum_after_inserting_patches]
```
Results
```
Files have the same content: libtiff_13/tiff_read_rgba_fuzzer and libtiff_13/tiff_read_rgba_fuzzer
Files have the same content: openssl_5/asn1parse and openssl_5/asn1parse
Files have the same content: openssl_5/bignum and openssl_5/bignum
Files have the same content: openssl_5/x509 and openssl_5/x509
Files have the same content: openssl_18/asn1parse and openssl_18/asn1parse
Files have the same content: openssl_18/bignum and openssl_18/bignum
Files have the same content: openssl_18/x509 and openssl_18/x509
Files have the same content: sqlite3_4/sqlite3_fuzz and sqlite3_4/sqlite3_fuzz
```

# Steps to run coverage experiments
1. To show all available CPUs: `lscpu --extended`. Notice that the CPUs with high `MAXMHZ` value have better performance. The CPUs with the same core ID have the same physical core. To maximize the CPU usage, we use one physical core for each fuzzing campaign and we choose the `MAXMHZ` value to be as high as possible.
2. The queue folder stores test inputs in file paths that look like `libpng_4_1/libpng_read_fuzzer/0/findings/queue` with the format `[benchmark_name]/[target_name]/[iteration_number]/findings/queue`.
3. We need to run llvm_cov to collect the coverage. Set up the corpus in the `Dockerfile`. For example, for ffd:
```
ARG corpus_name
ARG seed_path1=seed/ffd/${target_name}
ENV SEED 	${TARGET}/corpus/seed
USER root:root
RUN mkdir -p ${SEED}/ffd && chown magma:magma ${SEED}/ffd && chown magma:magma ${SEED}
COPY --chown=magma:magma ${magma_root}/${seed_path1} ${SEED}/ffd
USER magma:magma
```

# Experimental tips
1. When the inodes are exhausted, no more files or directories can be created even if there is enough disk space. 
2. Make sure to double check the configs in captainrc before running experiments. If the name of the working directory is not changed, the fuzzing data will be stored in the same directory `[benchmark_name]/[target_name]/` but the iteration number in `[benchmark_name]/[target_name]/[iteration_number]/` will increase by 1.
3. See corpus minimization results in [corpus_minimization_results.md](corpus_minimization_results.md)

## Notes for the raw fuzzing data
1. The build time for `libpng_4_1` is missing for aflgoexp because the target is pre-built when I first ran the experiments. However, we do not use the intrumentation time for aflgoexp in the figure because the difference between aflgo and aflgoexp is the `-c 0m ` configuration, which is the time from start when the algorithm enters exploitation.
2. The file `afl_sqlite3_20_1_sqlite3_fuzz_simple_fuzzer_stats` in `ContinuousFuzzBench/tools/process_data_tosem/simple_fuzzer_stats/afl` has no entries for the 7th and 8th iterations, as the `fuzzer_stats` files do not exist for these two iterations.
3. The fuzzing data for the benchmark `php_6_2` is missing for aflgo, aflplusplus, ffd. The fuzzing data for this benchmark is stored in the `exp/afl` GitHub branch.
4. We exclude libfuzzer when comparing the execution counts and the actual fuzzing time due to different logging methods.
5. During the 10-iteration fuzzing campaigns in the Docker container, we notice that sometimes one run is missed or skipped so that the scripts in `CICDBench/tools/benchd` can no longer work due to index errors. We need to set up the fuzzing experiments for the missing runs or rename the directories and files to make sure that the indices are from `0` to `9` in order to use the scripts to perform the survival analysis.
6. Need to rename the aflgoexp's fuzzing files because aflgoexp is essentially aflgo with a different config when fuzzing, so the fuzzing data is stored in files with aflgo as prefix names.
