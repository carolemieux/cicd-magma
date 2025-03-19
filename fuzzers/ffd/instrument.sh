#!/bin/bash
#set -e

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
# - env TARGET: path to target work dir
# - env MAGMA: path to Magma support files
# - env OUT: path to directory where artifacts are stored
# - env CFLAGS and CXXFLAGS must be set to link against Magma instrumentation
##

mkdir $TARGET/repo/temp
export TMP_DIR=$TARGET/repo/temp

export CC="$FUZZER/repo/afl-clang-fast"
export CXX="$FUZZER/repo/afl-clang-fast++"

# Set aflgo-instrumentation flags
export COPY_CFLAGS=$CFLAGS
export COPY_CXXFLAGS=$CXXFLAGS

# Set targets for specified bugs
echo "Setting targets"
$FUZZER/fetchtargets.sh

if [[ ! -f $TMP_DIR/BBtargets.txt ]] ; then
    echo "File BBtargets.txt not found, aborting."
    exit 1
fi

# Print extracted targets.
echo "BBtargets:"
cat $TMP_DIR/BBtargets.txt

source "$TARGET/configrc"
export LIBS="$LIBS $OUT/afl_driver.a -lstdc++"

"$MAGMA/build.sh"
echo "Magma build is done"

# Set ffd-instrumentation flags
export ADDITIONAL="-target_locations=$TMP_DIR/BBtargets.txt"
export CFLAGS="$CFLAGS $ADDITIONAL"
export CXXFLAGS="$CXXFLAGS $ADDITIONAL"
export WAYPOINTS="diff"

"$TARGET/build.sh"
echo "Target build is done"

echo "Instrumentation is done"
