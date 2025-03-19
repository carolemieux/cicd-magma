#!/bin/bash
set -e

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
##

if [ ! -d "$FUZZER/FishFuzz" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

mkdir $FUZZER/llvm/binutils/build && cd $FUZZER/llvm/binutils/build && \
        CFLAGS="" CXXFLAGS="" CC=gcc CXX=g++ \
        ../configure --enable-gold --enable-plugins --disable-werror && \
        make all-gold -j$(nproc)

cd $FUZZER/llvm/ && mkdir build && cd build &&\
    CFLAGS="" CXXFLAGS="" CC=gcc CXX=g++ \
    cmake -DCMAKE_BUILD_TYPE=Release \
          -DLLVM_BINUTILS_INCDIR=$FUZZER/llvm/binutils/include \
          -DLLVM_ENABLE_PROJECTS="compiler-rt;clang" \
          -DLLVM_ENABLE_RUNTIMES="libcxx;libcxxabi" ../llvm && \
    make -j$(nproc) && \
    cp $FUZZER/llvm/build/lib/LLVMgold.so //usr/lib/bfd-plugins/ && \
    cp $FUZZER/llvm/build/lib/libLTO.so //usr/lib/bfd-plugins/

export LLVM_CONFIG=llvm-config

# make sure our modified clang-12 is called before clang-15, which is in /usr/local/bin
export PATH="$FUZZER/llvm/build/bin:${PATH}"
export LD_LIBRARY_PATH="$FUZZER/llvm/build/lib/x86_64-unknown-linux-gnu/"

# Build without Python support as we don't need it.
# Set AFL_NO_X86 to skip flaky tests.
cd $FUZZER/FishFuzz/ && \
    unset CFLAGS CXXFLAGS CC CXX && \
    git checkout 40947508037b874020c8dd1251359fecaab04b9d src/afl-fuzz-bitmap.c && \
    export AFL_NO_X86=1 && \
    make clean && \
    PYTHON_INCLUDE=/ make && \
    # make -C dyncfg && \
    chmod +x fish_mode/distance/*.py && \
    make install

wget https://raw.githubusercontent.com/llvm/llvm-project/5feb80e748924606531ba28c97fe65145c65372e/compiler-rt/lib/fuzzer/afl/afl_driver.cpp -O $FUZZER/FishFuzz/afl_driver.cpp && \
    clang++ -stdlib=libc++ -std=c++11 -O2 -c $FUZZER/FishFuzz/afl_driver.cpp -o $FUZZER/FishFuzz/afl_driver.o && \
    ar r $FUZZER/libAFLDriver.a $FUZZER/FishFuzz/afl_driver.o $FUZZER/FishFuzz/afl-compiler-rt.o

