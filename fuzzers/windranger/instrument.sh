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
# Requires the tmp dir
mkdir -p $TARGET/repo/temp
export WR_TMP_DIR="$TARGET/repo/temp"
export SIG_WR_TMP_DIR="$TARGET/repo/temp"

# Set AFL compilers
export CC="$FUZZER/repo/afl-clang-fast"
export CXX="$FUZZER/repo/afl-clang-fast++"

# Make sure all compilation tools are using the LLVM 12 tool chain
export AS="$(which llvm-as-12)"
export RANLIB="$(which llvm-ranlib-12)"
export AR="$(which llvm-ar-12)"
export LD="$(which ld.lld-12)"
export NM="$(which llvm-nm-12)"
export AFL_CC=clang-12
export AFL_CXX=clang++-12

export LIBS="$LIBS -l:afl_driver.o -lstdc++"

# # Use WindRanger to compile the target program
# $CC prog1.c -o prog1

"$MAGMA/build.sh"

echo "Magma build done"

source $TARGET/configrc
#TODO: if PATCHES include more than one patch, it will fail. Fix later

cp $FUZZER/targets/${PATCHES} $WR_TMP_DIR/BBtargets.txt
# Set the targets, the file BBtargets.txt has the same format as that in AFLGo
export WR_BB_TARGETS="$WR_TMP_DIR/BBtargets.txt"
# Set the programs used for directed fuzzing, separated by ':'
export WR_TARGETS="$PROGRAM" # or "::" for all programs

"$TARGET/build.sh"

echo "Target build done"

# NOTE: We pass $OUT directly to the target build.sh script, since the artifact
#       itself is the fuzz target. In the case of Angora, we might need to
#       replace $OUT by $OUT/fast and $OUT/track, for instance.