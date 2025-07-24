#!/bin/bash

# Check if the required parameters are provided
if [ $# -ne 4 ]; then
  echo "Usage: $0 repo_dir git_url commit_sha tmp_dir"
  exit 1
fi

repo_dir="$1"
git_url="$2"
commit_sha="$3"
tmp_dir="$4"

mkdir -p "$repo_dir"

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

git diff -U0 HEAD^ HEAD > tmp_commit.diff
cat tmp_commit.diff | $tmp_dir/showlinenum.awk show_header=0 path=1 | grep -e "\.[ch]:[0-9]*:+" -e "\.cpp:[0-9]*:+" -e "\.cc:[0-9]*:+" | cut -d+ -f1 | rev | cut -c2- | rev > "$tmp_dir"/"$repo_dir"_BBtargets.txt

echo $(cat "$tmp_dir"/"$repo_dir"_BBtargets.txt | wc -l)

# Clean up
cd ..
rm -rf "$repo_dir"
