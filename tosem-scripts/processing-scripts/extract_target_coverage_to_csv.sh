#!/bin/bash

coverage_dir=$1
mode=$2

if [ $# -ne 1 ]; then
	echo "usage: $0 coverage_results_directory"
  echo "This script outputs to stdout."
	echo "coverage_results_directory should contain all the [...]_target_file_coverage.txt "
	echo "you are interested in analyzing. (this script will ignore [...]_total_coverage.txt)"
	exit 1
fi



postfix="target_file_coverage.txt"
# from https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
tgt_names=$script_dir/resources/target_to_fns.csv
pushd $coverage_dir
while IFS=, read -r tech bench; do
  # Turn the set of target functions (because there may be more than one) into an
  # or regex for grep
	tget_grep=$(grep $bench $tgt_names | awk -F, '{$1=""; print}' | tr ' ' '|' )
	tget_grep=${tget_grep:1}
	for cov_file in ${tech}_${bench}_*${postfix}; do
	  # Manually compute percentage coverage for the functions being targeted. As it is not
	  # multiplied by 100, it is between 0 and 1 rather than a proper percentage.
		grep -E $tget_grep $cov_file | awk 'BEGIN{found_lines=0}{found_lines=1;tot+=$5; cov+=$5-$6} END {if (found_lines == 1) {print cov/tot} else {print "-"}}'
	done  | xargs echo $tech $bench | tr ' ' ',' 
done < <(ls -1 | sed 's|\([^_]*\)_\([a-zA-Z0-9]\+_[0-9]\+_[0-9]\+\).*|\1,\2|' | sort | uniq)

popd 
