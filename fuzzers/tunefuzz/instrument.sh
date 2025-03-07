#!/bin/bash
set -e

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
# - env TARGET: path to target work dir
# - env MAGMA: path to Magma support files
# - env OUT: path to directory where artifacts are stored
# - env CFLAGS and CXXFLAGS must be set to link against Magma instrumentation
##

export CC="$FUZZER/FishFuzz/afl-clang-fast"
export CXX="$FUZZER/FishFuzz/afl-clang-fast++"


export LLVM_CONFIG=llvm-config
export PATH="$FUZZER/llvm/build/bin:${PATH}"
export LD_LIBRARY_PATH="$FUZZER/llvm/build/lib/x86_64-unknown-linux-gnu/"

export LIBS="$LIBS -lc++ -lc++abi"
export FUZZER_LIB="$FUZZER/FishFuzz/afl_driver.o"
export LIB_FUZZING_ENGINE=$FUZZER_LIB

export FUZZ_OUT="$OUT/tunefuzz"
export LDFLAGS="$LDFLAGS -L$FUZZ_OUT"

export USE_FF_INST=1
export TMP_DIR="$FUZZ_OUT/TEMP"
export FF_TMP_DIR="$FUZZ_OUT/TEMP"

mkdir -p $FUZZ_OUT
mkdir -p $TMP_DIR

mkdir -p "$TMP_DIR/idlog"
mkdir -p "$TMP_DIR/cg"
mkdir -p "$TMP_DIR/fid"
touch "$TMP_DIR/idlog/fid" "$TMP_DIR/idlog/targid"

"$MAGMA/build.sh"
"$TARGET/build.sh"

python3 $FUZZER/FishFuzz/fish_mode/distance/match_function.py -i $FF_TMP_DIR
python3 $FUZZER/FishFuzz/fish_mode/distance/calculate_all_distance.py -i $FF_TMP_DIR

# # NOTE: We pass $OUT directly to the target build.sh script, since the artifact
# #       itself is the fuzz target. In the case of Angora, we might need to
# #       replace $OUT by $OUT/fast and $OUT/track, for instance.
