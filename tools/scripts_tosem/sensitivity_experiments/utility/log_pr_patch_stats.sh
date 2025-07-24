#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

patch_dir="$1"

# Sanity check
if [ ! -d "$patch_dir" ]; then
  echo "$patch_dir is not a directory."
  exit 1
fi

for patch_file in "$patch_dir"/*; do

  if [ ! -f "$patch_file" ]; then
    continue
  fi

  # Extract the base filename without extension for CSV output
  filename=$(basename "$patch_file")
  output_csv="${filename%.*}_patch_stats.csv"

  # Write CSV header
  echo "Patch_URL,Commit_Count,Files_Changed,Insertions,Deletions,Total_Changes" > "$output_csv"

  # Read line by line
  while IFS= read -r patch_url; do

    if [[ -z "$patch_url" ]]; then
      continue
    fi

    patch_file="temp_patch"

    # Download the patch using curl
    curl -s "$patch_url" -o "$patch_file"

    if [ $? -ne 0 ]; then
      echo "Failed to download: $patch_url"
      continue
    fi

    # Use diffstat to extract patch statistics
    diff_output=$(diffstat "$patch_file")

    echo "$patch_url"
    echo "$diff_output"

    # Extract the number of files changed, insertions, and deletions from the diffstat output
    files_changed=$(echo "$diff_output" | grep -o '[0-9]* file' | awk '{print $1}')
    insertions=$(echo "$diff_output" | grep -o '[0-9]* insertions' | awk '{print $1}')
    deletions=$(echo "$diff_output" | grep -o '[0-9]* deletion' | awk '{print $1}')
    commit_count=$(cat "$patch_file" | grep -c '^From: ')
    
    # Set to 0 if not found
    files_changed=${files_changed:-0}
    insertions=${insertions:-0}
    deletions=${deletions:-0}
    total_changes=$((insertions + deletions))

    # Append the results to the CSV file
    echo "$patch_url,$commit_count,$files_changed,$insertions,$deletions,$total_changes" >> "$output_csv"

    # Clean up the temporary patch file
    rm -f "$patch_file"

  done < "$patch_file"

  # Inform the user where the CSV is stored for each file
  echo "CSV output written to: $output_csv"
done
