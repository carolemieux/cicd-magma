#!/bin/bash

# Sanity check
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <patch_dir> <tmp_dir>"
    exit 1
fi

patch_dir=$1           
tmp_dir=$2   

for patchfile in "$patch_dir"/*.patch; do
    basename=$(basename "$patchfile" .patch)
    # get the targets
    cat "$patchfile" | showlinenum.awk show_header=0 path=1 | grep -e "\.[ch]:[0-9]*:+" -e "\.cpp:[0-9]*:+" -e "\.cc:[0-9]*:+" -e "\.c\.in:[0-9]*:+" | cut -d+ -f1 | rev | cut -c2- | rev > "$tmp_dir/${basename}_output.txt"
done
