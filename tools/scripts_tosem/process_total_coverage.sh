#!/bin/bash -e

# do not execute multiple times for a single coverage directory, otherwise the results will accumulate

if [ "$#" -ne 2 ]; then
    echo "Usage: <script_name> <coverage_path> <output_path>"
    exit 1
fi

coverage_path=$1
output_path=$2

mkdir -p $output_path

if [[ "$coverage_path" == *"-aflgo-"* ]]; then 
    awk_start_index=1
    cut_start_index=4
else 
    awk_start_index=2
    cut_start_index=5
fi

for log_path in "$coverage_path"/ar/*/*/*/*/coverage/*total_coverage.txt
do  
    echo $log_path

    if [[ "$coverage_path" == *"-aflgo-"* ]]; then 
        fuzzer_name='aflgo'
    else 
        fuzzer_name=$(basename $log_path | awk -F'_' '{print $1}')
    fi
    target_name=$(basename $log_path | awk -v i="$awk_start_index" -F'_' '{print $(i) "_" $(i+1) "_" $(i+2)}')
    program_name=$(basename $log_path | cut -d '_' -f"$cut_start_index"- | sed -r 's/_[0-9]_total_coverage.txt//g')
    # the third last field
    iter_num=$(basename $log_path | awk -F'_' '{print $(NF-2)}')

    echo $fuzzer_name, $target_name, $program_name, $iter_num

    mkdir -p $output_path/$fuzzer_name

    if [[ ! -f "$output_path/$fuzzer_name/$fuzzer_name"_"$target_name"_"$program_name"_total_coverage ]]; then 
        echo "TARGET,PROGRAM,ITER,Filename,Regions,Missed_Regions,Cover,Functions,Missed_Functions,Executed,Lines,Missed_Lines,Cover,Branches,Missed_Branches,Cover" > "$output_path/$fuzzer_name/$fuzzer_name"_"$target_name"_"$program_name"_total_coverage
    fi

    # output=$(tail -n 1 "$log_path" | sed -r 's/\s+/,/g')
    # special workaround for macOS
    output=$(tail -n 1 "$log_path" | sed -E 's/[[:space:]]+/,/g')
    echo $output
    echo "$target_name,$program_name,$iter_num,$output" >> "$output_path/$fuzzer_name/$fuzzer_name"_"$target_name"_"$program_name"_total_coverage
done;
