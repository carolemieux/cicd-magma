#!/bin/bash
set -e

##
# Pre-requirements:
# - env TARGET: path to target work dir
# - env OUT: path to directory where artifacts are stored
# - env CC, CXX, FLAGS, LIBS, etc...
##

if [ ! -d "$TARGET/repo" ]; then
    echo "fetch.sh must be executed first."
    exit 1
fi

cd "$TARGET/repo"
./autogen.sh
./configure --disable-shared --enable-ossfuzzers

export LIBS="$LIBS $FUZZER_LIB"
make -j$(nproc) clean
make ossfuzz/sndfile_fuzzer

cp -v ossfuzz/sndfile_fuzzer $OUT/
#cp ossfuzz/sndfile_fuzzer.0.0.*.bc $OUT/
if ls ossfuzz/sndfile_fuzzer.0.0.*.bc > /dev/null 2>&1; then 
    cp ossfuzz/sndfile_fuzzer.0.0.*.bc $OUT/
fi
