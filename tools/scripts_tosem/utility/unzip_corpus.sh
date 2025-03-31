#!/bin/bash
set -e

for i in {0..9}; do
    dir="/Volumes/GitRepo/aflgo-other-log/missing_build_time_log_for_aflgoexp/libpng_4_1/*/$i"
    # Use a loop to handle multiple matches
    for subdir in $dir; do
        if [[ -f "$subdir/ball.tar" ]]; then
            echo "Unzipping ball.tar in $subdir"
            tar -xf "$subdir/ball.tar" -C "$subdir"
            rm "$subdir/ball.tar"
        fi
    done
done
