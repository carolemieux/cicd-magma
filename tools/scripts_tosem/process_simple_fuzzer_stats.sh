#!/bin/bash -e

# make sure not to run the script multiple times for the same fuzzer, otherwise the data will accumulate in the same log file

if [ "$#" -ne 2 ]; then
    echo "Usage: <script_name> <log_dir> <output_dir>"
    exit 1
fi

log_dir="$1"
output_dir="$2"

mkdir -p $output_dir

if [[ $log_dir == *"aflpp"* || $log_dir == *"aflplusplus"* || $log_dir == *"tunefuzz"* ]]; then
    # because the fuzzing data for afl++ based fuzzers has an additional directory named "default"
    start_index=4
else
    start_index=4
fi

stats_path="$log_dir"/*/*/*

for log_path in $stats_path
do
    find "$log_path" -type f -name "fuzzer_stats" | while read stats_file; 
    do
        echo $stats_file
        fuzzer_name=$(echo $stats_file | awk -F'data' '{print $2}' | awk -v i="$start_index" -F'/' '{print $(i)}')
        target_name=$(echo $stats_file | awk -F'data' '{print $2}' | awk -v i="$start_index" -F'/' '{print $(i+1)}')
        program_name=$(echo $stats_file | awk -F'data' '{print $2}' | awk -v i="$start_index" -F'/' '{print $(i+2)}')
        iter_num=$(echo $stats_file | awk -F'data' '{print $2}' | awk -v i="$start_index" -F'/' '{print $(i+3)}')

        if [ -f "$stats_file" ]; then 
            stats="$fuzzer_name,$target_name,$program_name,$iter_num,$(awk '/start_time/ || /execs_done/' $stats_file | cut -c 21- | tr '\n' ',' | sed 's/\,$//')" 
        else 
            stats="$fuzzer_name,$target_name,$program_name,$iter_num"
        fi 

        mkdir -p "$output_dir/$fuzzer_name"
        output_file_name="$output_dir/$fuzzer_name/$fuzzer_name"_"$target_name"_"$program_name"_simple_fuzzer_stats
        
        if ! [ -f "$output_file_name" ]; then 
            echo "fuzzer,target,program,iteration,start_time,execs_done" > "$output_file_name"
        fi
        echo "$stats" >> "$output_file_name"
    done 
done
