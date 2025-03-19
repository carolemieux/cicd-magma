#!/bin/bash

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
# - env TARGET: path to target work dir
# - env OUT: path to directory where artifacts are stored
# - env SHARED: path to directory shared with host (to store results)
# - env PROGRAM: name of program to run (should be found in $OUT)
# - env ARGS: extra arguments to pass to the program
# - env FUZZARGS: extra arguments to pass to the fuzzer
##

mkdir -p "$SHARED/findings"

export AFL_SKIP_CPUFREQ=1
export AFL_NO_AFFINITY=1

export AFL_SKIP_CRASHES=1
export AFL_FAST_CAL=1

# time to exploitation set to 0 minute
"$FUZZER/repo/afl-2.57b/afl-fuzz" -m none -t 10000 -z exp -c 0m -i "$SEED" -o "$SHARED/findings" \
    $FUZZARGS -- "$OUT/$PROGRAM" $ARGS 2>&1
