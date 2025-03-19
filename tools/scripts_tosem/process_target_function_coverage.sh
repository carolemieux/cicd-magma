#!/bin/bash -e

# do not execute multiple times for a single coverage directory, otherwise the results will accumulate

if [ "$#" -ne 3 ]; then
    echo "Usage: <script_name> <path_to_csv_file> <coverage_path> <output_path>"
    exit 1
fi

csv_file="$1"
coverage_path="$2"
output_path="$3"

if [[ "$coverage_path" == *"-aflgo-"* ]]; then 
    awk_start_index=1
    cut_start_index=4
else 
    awk_start_index=2
    cut_start_index=5
fi

echo "Processing $coverage_path..."

while IFS=',' read -r function_name file_name; do
    echo $function_name, $file_name              
    base_name=$(echo $file_name | awk -F'_' '{print $2 "_" $3 "_" $4}' )    

    if [[ -n "$base_name" ]]; then

        echo "Searching for files matching pattern $base_name..."
        files=$(find "$coverage_path" -type f -name "*$base_name*_*_target_file_coverage*")
        
        for file in $files; do
            if [[ -f "$file" ]]; then
                cov_file_name=$(basename $file)
                echo "Processing $cov_file_name"
                if [[ "$coverage_path" == *"-aflgo-"* ]]; then 
                    fuzzer_name='aflgo'
                else 
                    fuzzer_name=$(echo $cov_file_name | awk -F'_' '{print $1}')
                fi
                target_name=$(echo $cov_file_name | awk -v i="$awk_start_index" -F'_' '{print $(i) "_" $(i+1) "_" $(i+2)}')
                program_name=$(echo $cov_file_name | cut -d '_' -f"$cut_start_index"- | sed -r 's/_[0-9]_target_file_coverage.txt//g')
                # the fourth last field
                iter_num=$(echo $cov_file_name | awk -F'_' '{print $(NF-3)}')

                echo $fuzzer_name, $target_name, $program_name, $iter_num

                mkdir -p $output_path/$fuzzer_name
                result_path="${output_path}/${fuzzer_name}/${fuzzer_name}_${target_name}_${program_name}_target_function_coverage"

                if [[ ! -f "$result_path" ]]; then 
                    echo "TARGET,PROGRAM,ITER,Filename,Regions,Miss,Cover,Lines,Miss,Cover,Branches,Miss,Cover" > "$result_path"
                fi

                output=$(grep -w "$function_name" "$file" | sed -E 's/[[:space:]]+/,/g')
                echo "$target_name,$program_name,$iter_num,$output" >> "$result_path"

            fi
        done
    fi

done < "$csv_file"
