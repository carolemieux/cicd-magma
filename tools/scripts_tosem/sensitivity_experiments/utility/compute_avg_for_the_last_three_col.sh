#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <input_dir>"
  exit 1
fi

input_dir="$1"

# Loop through all CSV files in the specified directory
for csv_file in "$input_dir"/*.csv; do

    # Check if the file exists
    if [[ ! -f "$csv_file" ]]; then
        echo "No csv files found in the directory."
        exit 1
    fi

    # Calculate the average 
    #col_avg=$(awk -F',' '{sum+=$(NF-4); count++} END {if (count > 0) print sum/count}' "$csv_file")
    #col_avg0=$(awk -F',' '{sum+=$(NF-3); count++} END {if (count > 0) print sum/count}' "$csv_file")
    col_avg1=$(awk -F',' '{sum+=$(NF-2); count++} END {if (count > 0) print sum/count}' "$csv_file")
    col_avg2=$(awk -F',' '{sum+=$(NF-1); count++} END {if (count > 0) print sum/count}' "$csv_file")
    col_avg3=$(awk -F',' '{sum+=$NF; count++} END {if (count > 0) print sum/count}' "$csv_file")

    # Save the results
    echo "$col_avg1,$col_avg2,$col_avg3" >> "$csv_file"
    echo "Results saved to $csv_file"
done
