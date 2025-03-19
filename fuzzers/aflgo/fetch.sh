#!/bin/bash
set -e

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
##

git clone --no-checkout https://github.com/aflgo/aflgo.git "$FUZZER/repo"
git -C "$FUZZER/repo" checkout fa125da5d70621daf7141c6279877c97708c8c1f

cp "$FUZZER/src/afl_driver.cpp" "$FUZZER/repo/afl_driver.cpp"

mkdir "$FUZZER/repo/instrument/llvm_tools"
cd "$FUZZER/repo/instrument/llvm_tools"

wget -O llvm-11.0.0.src.tar.xz https://github.com/llvm/llvm-project/releases/download/llvmorg-11.0.0/llvm-11.0.0.src.tar.xz
tar -xf llvm-11.0.0.src.tar.xz
mv      llvm-11.0.0.src        llvm

wget -O  clang-11.0.0.src.tar.xz https://github.com/llvm/llvm-project/releases/download/llvmorg-11.0.0/clang-11.0.0.src.tar.xz
tar -xf  clang-11.0.0.src.tar.xz
mv       clang-11.0.0.src        clang

wget -O compiler-rt-11.0.0.src.tar.xz https://github.com/llvm/llvm-project/releases/download/llvmorg-11.0.0/compiler-rt-11.0.0.src.tar.xz
tar -xf compiler-rt-11.0.0.src.tar.xz
mv      compiler-rt-11.0.0.src        compiler-rt

mkdir -p "$FUZZER/repo/instrument/llvm_tools/build"
