#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 input.csv"
  exit 1
fi

input_csv="$1"

{
  read # Skip the header
  while IFS=',' read -r git_url commit_sha; do

    # get repo name and output file name
    repo_name=$(basename "$git_url" .git)
    commit_csv="../${repo_name}_commit_stats.csv"

    # Initialize the commit-level CSV file with headers
    echo "Commit_Hash,Added,Deleted,Total" > "$commit_csv"

    # Call the secondary script and pass the parameters
    echo "Processing $repo_name..."
    ./process_commit_history.sh "$git_url" "$commit_sha" 11 >> "$commit_csv"
  done
} < "$input_csv"  # Read from the input CSV

echo "Results saved."
