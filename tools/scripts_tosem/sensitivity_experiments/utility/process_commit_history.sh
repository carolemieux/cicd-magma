#!/bin/bash

# Check if the required parameters are provided
if [ $# -ne 3 ]; then
  echo "Usage: $0 git_url commit_sha num_commit"
  exit 1
fi

git_url="$1"
commit_sha="$2"
num_commit="$3"

# Create a temporary directory for cloning the repo
repo_dir=$(mktemp -d)

# Clone the repository 
git clone "$git_url" "$repo_dir" > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Failed to clone $git_url"
  exit 1
fi

# Go to the repo directory
# Do not use pushd popd to avoid extra log
cd "$repo_dir" || exit 1

# Checkout to the specific commit
git checkout "$commit_sha" > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Failed to checkout to commit $commit_sha in $git_url" 
  # Clean up
  cd ..
  rm -rf "$repo_dir"
  exit 1
fi

# Get the last n commits and compute the stats
# Note that this will only output the earliest commit if multiple consecutive commits modified the same file
# It will skip the last commit output due to the check of $0
git log -n $num_commit --pretty=format:'%H' --numstat | awk '
  BEGIN { added=0; deleted=0; }
  NF == 1 { commit=$1; next }
  { added+=$1; deleted+=$2 }
  { if ($0 == "") { print commit "," added "," deleted "," (added + deleted); added=0; deleted=0; } }
' 
# Clean up
cd ..
rm -rf "$repo_dir"
