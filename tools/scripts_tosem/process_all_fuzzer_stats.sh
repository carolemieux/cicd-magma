#!/bin/bash -e

if [ "$#" -ne 3 ]; then 
    echo "Usage: <script_name> <script_to_execute> <data_dir> <output_dir>"
    exit 1
fi

script="$1"
data_dir="$2"
output_dir="$3"

declare -a fuzzers=("afl" "aflgo" "aflgoexp" "aflplusplus" "ffd" "tunefuzz")

for fuzzer in "${fuzzers[@]}"
do
    full_data_path="$data_dir/$fuzzer"
    bash "$script" "$full_data_path" "$output_dir"
done
