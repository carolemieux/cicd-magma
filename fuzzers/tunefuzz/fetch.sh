#!/bin/bash
set -e

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
##

git clone https://github.com/kdsjZh/Fishpp $FUZZER/FishFuzz && \
    cd $FUZZER/FishFuzz && \
    git checkout be113d6a9d27c0b574d083f2d827d1e6c551435d || \
    true

mkdir -p $FUZZER/build && \
    git clone \
        https://github.com/llvm/llvm-project $FUZZER/llvm

git clone \
        --depth 1 \
        --branch binutils-2_40-branch \
    https://sourceware.org/git/binutils-gdb.git $FUZZER/llvm/binutils && \
    cd $FUZZER/llvm/ && git checkout bf7f8d6fa6f460bf0a16ffec319cd71592216bf4 && \
    git apply $FUZZER/FishFuzz/fish_mode/llvm_patch/llvm-15.0/llvm-15-asan.diff && \
    cp $FUZZER/FishFuzz/fish_mode/llvm_patch/llvm-15.0/FishFuzzAddressSanitizer.cpp llvm/lib/Transforms/Instrumentation/

