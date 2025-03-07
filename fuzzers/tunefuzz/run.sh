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

if nm "$OUT/tunefuzz/$PROGRAM" | grep -E '^[0-9a-f]+\s+[Ww]\s+main$'; then
    ARGS="-"
fi

export PATH="$FUZZER/llvm/build/bin:${PATH}"
export LD_LIBRARY_PATH="$FUZZER/llvm/build/lib/x86_64-unknown-linux-gnu/"

export AFL_NO_UI=1
export AFL_SKIP_CPUFREQ=1
export AFL_NO_AFFINITY=1
export AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1
export AFL_SKIP_CRASHES=1
export AFL_SHUFFLE_QUEUE=1

export FUZZ_NEARBY=1
export AFL_FAST_CAL=1
export AFL_NO_WARN_INSTABILITY=1
export AFL_IGNORE_UNKNOWN_ENVS=1

export AFL_DISABLE_TRIM=1
export AFL_CMPLOG_ONLY_NEW=1

export TMP_DIR="$OUT/tunefuzz/TEMP"
export FF_TMP_DIR="$OUT/tunefuzz/TEMP"

# export AFL_MAP_SIZE=256000
# export AFL_DRIVER_DONT_DEFER=1

mkdir -p "$SHARED/findings"

flag_cmplog=(-m none -c "$OUT/cmplog/$PROGRAM")

"$FUZZER/FishFuzz/afl-fuzz" -i "$TARGET/corpus/$PROGRAM" -o "$SHARED/findings" \
    "${flag_cmplog[@]}" -d \
    $FUZZARGS -- "$OUT/tunefuzz/$PROGRAM" $ARGS 2>&1
