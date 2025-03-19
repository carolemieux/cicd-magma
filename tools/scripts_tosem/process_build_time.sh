#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: <script_name> <log_dir> <output_dir>"
    exit 1
fi

log_dir="$1"
output_dir="$2"

mkdir -p $output_dir

for file in $log_dir/*/*/*build.log; do
  echo $file
  log_name=$(basename $file)
  fuzzer_name=$(echo $log_name | awk -F'_' '{print $1}')

  if [[ ! -f $output_dir/"$fuzzer_name"_build_time ]]; then 
      echo "benchmark,time,file_name" > $output_dir/"$fuzzer_name"_build_time
  fi

  time=$(grep -B 2 'exporting to image' "$file" | grep 'DONE' | sed 's/.*DONE //')

  if [ -n "$time" ]; then
    benchmark_name=$(basename $file | awk -F'_' '{print $2"_"$3"_"$4}')
    echo "$benchmark_name,$time,$file" >> $output_dir/"$fuzzer_name"_build_time
  fi
done
