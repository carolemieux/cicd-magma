#!/bin/bash -e

if [ "$#" -ne 3 ]; then 
    echo "Usage: <script_name> <script_to_execute> <data_dir> <output_dir>"
    exit 1
fi

script="$1"
data_dir="$2"
output_dir="$3"

mkdir -p "$output_dir"

for coverage_path in "$data_dir"/*coverage*
do  
    echo $coverage_path
    bash "$script" target_functions.csv "$coverage_path" "$output_dir"
done;
