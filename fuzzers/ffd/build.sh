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

pushd "$FUZZER/repo"
make

export CC=clang
export AFL_CC=clang

make llvm-domains

pushd llvm_mode
make
popd

# compile afl_driver.cpp
clang++ $CXXFLAGS -std=c++11 -c "afl_driver.cpp" -o "$OUT/afl_driver.o"
ar r $OUT/afl_driver.a $OUT/afl_driver.o
popd
