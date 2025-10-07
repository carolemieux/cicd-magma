#!/bin/bash
set -e

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
##

if [ ! -d "$FUZZER/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$FUZZER/repo"

# Environment variables
CC=clang-12
CXX=clang++-12
LLVM_CONFIG=llvm-config-12
export AFL_REAL_LD="ld.lld-12"

mkdir -p $TARGET/repo/temp
export WR_TMP_DIR="$TARGET/repo/temp"
export SIG_WR_TMP_DIR="$TARGET/repo/temp"

make clean 
make all
echo "make1 done yay"
pushd llvm_mode 
make clean 
make all
popd

# compile afl_driver.cpp
"./afl-clang-fast++" $CXXFLAGS -std=c++11 -c "afl_driver.cpp" -fPIC -o "$OUT/afl_driver.o"
echo "Fuzzer build done"