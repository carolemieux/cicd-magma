#!/bin/bash -e

if [ "$#" -ne 2 ]; then 
    echo "Usage: <script_name> <script_to_execute> <data_dir>"
    exit 1
fi

script="$1"
data_dir="$2"

declare -a fuzzers=("afl" "aflgo" "aflgoexp" "aflplusplus" "ffd" "tunefuzz")

for fuzzer in "${fuzzers[@]}"
do
    full_data_path="$data_dir/$fuzzer"
    bash "$script" "$full_data_path" "../process_data_tosem/original_experiments/simple_fuzzer_stats"
done
