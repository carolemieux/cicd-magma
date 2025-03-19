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

cd "$FUZZER/repo/instrument/llvm_tools/build"

cmake -G "Ninja" \
      -DCMAKE_BUILD_TYPE=Release \
      -DLLVM_TARGETS_TO_BUILD="X86" \
      -DLLVM_BINUTILS_INCDIR=/usr/include \
      -DLLVM_ENABLE_PROJECTS="clang;compiler-rt" \
      -DLLVM_BUILD_TESTS=OFF \
      -DLLVM_INCLUDE_TESTS=OFF \
      -DLLVM_BUILD_BENCHMARKS=OFF \
      -DLLVM_INCLUDE_BENCHMARKS=OFF \
      -DCMAKE_INSTALL_PREFIX=$FUZZER/repo/instrument/llvm_tools/build \
      ../llvm
ninja; ninja install
echo "LLVM build done"

cd "$FUZZER/repo"
#######################################
### Install LLVMgold in bfd-plugins ###
#######################################
mkdir -p /usr/lib/bfd-plugins
ls $FUZZER/repo/instrument/llvm_tools/build/lib
cp $FUZZER/repo/instrument/llvm_tools/build/lib/libLTO.so /usr/lib/bfd-plugins
cp $FUZZER/repo/instrument/llvm_tools/build/lib/LLVMgold.so /usr/lib/bfd-plugins

##############################
### Build AFLGo components ###
##############################
export PATH="$FUZZER/repo/instrument/llvm_tools/build/bin:$PATH"
export CXX=`which clang++`
export CC=`which clang`
export LLVM_CONFIG=`which llvm-config`

cd "$FUZZER/repo/afl-2.57b"
make clean all

cd "$FUZZER/repo/instrument"
make clean all

cd "$FUZZER/repo/distance/distance_calculator"
cmake ./
cmake --build ./

# compile afl_driver.cpp
cd "$FUZZER/repo"
clang++ $CXXFLAGS -std=c++11 -c "afl_driver.cpp" -o "$OUT/afl_driver.o"
ar r $OUT/afl_driver.a $OUT/afl_driver.o

echo "AFLGo build is done (yeah!)"
