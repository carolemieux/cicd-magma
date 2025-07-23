#!/bin/bash

# Sanity check
if [ $# -lt 2 ]; then
  echo "Usage: $0 output_directory patch_directory1 [...]"
  exit 1
fi

output_directory="$1"
mkdir -p "$output_directory"

# Shift the arguments to the next
shift  
# Loop through each patch directory 
for patch_directory in "$@"; do

  if [ ! -d "$patch_directory" ]; then
    echo "Patch directory $patch_directory does not exist."
    continue
  fi
  
  # Prepare the output name
  dir_name=$(echo "$patch_directory" | awk -F'/' '{print $(NF-2)}' | cut -d'_' -f1)
  output_csv="$output_directory/${dir_name}_patches.csv"

  # Create the header
  echo "Patch,Added,Deleted,Total" > "$output_csv"

  # Process each patch file
  for patchfile in "$patch_directory"/*.patch; do

    # Check if there are any patch files
    if [ ! -e "$patchfile" ]; then
      echo "No patch files found in $patch_directory."
      continue
    fi
    
    # Get the number of added lines, starting with + but not ++)
    added_lines=$(grep -c '^[+][^+]' "$patchfile")
    # Get the number of deleted lines, starting with - but not --)
    deleted_lines=$(grep -c '^-[^-]' "$patchfile")
    total_changes=$((added_lines + deleted_lines))

    echo "$(basename "$patchfile"),$added_lines,$deleted_lines,$total_changes" >> "$output_csv"
  done

  echo "Results saved to $output_csv."
done
