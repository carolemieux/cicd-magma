#!/bin/bash

# Sanity check
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <original_target_file> <initial_target> <output_file>"
    exit 1
fi

original_target_file=$1
initial_target=$2
output_file=$3

> $output_file

# Get the starting line number 
start_line=$(cut -d':' -f2 "$initial_target")

# Get the starting line number  from original_target_file 
previous_line_num=$(head -n 1 "$original_target_file" | cut -d':' -f2)

# Initialize the first target LOC in the output
current_target=$start_line

# Process each line in original_target_file
while read -r line; do
    # Extract the line number from original_target_file
    current_line_num=$(echo "$line" | cut -d':' -f2)
    # Calculate the gap between the current and previous LOC
    gap=$((current_line_num - previous_line_num))
    current_target=$((current_target + gap))
    # Store the results
    echo "sqlite3.c:$current_target" >> $output_file

    previous_line_num=$current_line_num
    
done < "$original_target_file"

echo "Output generated in $output_file"
