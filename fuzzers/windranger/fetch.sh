#!/bin/bash
set -e

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
##

git clone --no-checkout --recurse-submodules https://github.com/Mem2019/WindRanger.git "$FUZZER/repo"
git -C "$FUZZER/repo" checkout a87ea5d33845e1e2a9c7375fdc1e951293540dd3
pushd "$FUZZER/repo"
git submodule update --init --recursive
popd
cp "$FUZZER/src/afl_driver.cpp" "$FUZZER/repo/afl_driver.cpp"