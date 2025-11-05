#!/bin/bash

coverage_dir=$1

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 coverage_results_directory"
  exit 1
fi

pushd $coverage_dir > /dev/null
while IFS=, read -r tech bench; do
        for cov_file in ${tech}_${bench}_*total_coverage.txt; do
             tail -n 1 $cov_file | awk '{print $13}' | tr -d '%'
        done | xargs echo $tech $bench | tr ' ' ','
done < <(ls -1 | sed 's|\([^_]*\)_\([a-zA-Z0-9]\+_[0-9]\+_[0-9]\+\).*|\1,\2|' | sort | uniq)
popd > /dev/null