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

mkdir -p $TARGET/repo/temp
export TMP_DIR=$TARGET/repo/temp

export PATH="$FUZZER/repo/instrument/llvm_tools/build/bin:$PATH"
export LD_LIBRARY_PATH="$FUZZER/repo/instrument/llvm_tools/build/lib/:$FUZZER/repo/bin/lib:$LD_LIBRARY_PATH"

export CC="$FUZZER/repo/instrument/afl-clang-fast"
export CXX="$FUZZER/repo/instrument/afl-clang-fast++"

# Set aflgo-instrumentation flags
export COPY_CFLAGS=$CFLAGS
export COPY_CXXFLAGS=$CXXFLAGS

# Set targets for specified bugs
(
    echo "Setting targets"
    $FUZZER/fetchtargets.sh
    # Print targets
    echo "BBtargets:"
    cat $TMP_DIR/BBtargets.txt
)

(
    # Generate CG and intra-procedural CFGs from program
    echo "Generating CG"

    source "$TARGET/configrc"
    export LIBS="$LIBS $OUT/afl_driver.a -lstdc++"

    "$MAGMA/build.sh"
    echo "Magma build is done"

    # Set aflgo-instrumentation flags
    export ADDITIONAL="-targets=$TMP_DIR/BBtargets.txt -outdir=$TMP_DIR -flto -fuse-ld=gold -Wl,-plugin-opt=save-temps"
    export CFLAGS="$CFLAGS $ADDITIONAL"
    export CXXFLAGS="$CXXFLAGS $ADDITIONAL"

    "$TARGET/build.sh"
    echo "The first pass of target build is done"

    if [[ $TARGET == *"sqlite3"* ]]; then
        grep -n "#ifdef MAGMA_ENABLE_FIXES" $TARGET/repo/sqlite3.c | awk -F: '{print "sqlite3.c:" $1 }'
    fi

    if [[ ! -s $TMP_DIR/Ftargets.txt ]] ; then
        echo "File Ftargets.txt is empty, aborting"
        exit 1
    fi

    echo "Function targets:"
    cat $TMP_DIR/Ftargets.txt

    cat $TMP_DIR/BBnames.txt | grep -v "^$"| rev | cut -d: -f2- | rev | sort | uniq > $TMP_DIR/BBnames2.txt && mv $TMP_DIR/BBnames2.txt $TMP_DIR/BBnames.txt
    cat $TMP_DIR/BBcalls.txt | grep -Ev "^[^,]*$|^([^,]*,){2,}[^,]*$"| sort | uniq > $TMP_DIR/BBcalls2.txt && mv $TMP_DIR/BBcalls2.txt $TMP_DIR/BBcalls.txt

    # Only allows for one program at a time
    P="${PROGRAMS[0]}"
    echo "Generating distances for program $P"
    #$FUZZER/repo/distance/gen_distance_orig.sh $OUT $TMP_DIR $P
    $FUZZER/repo/distance/gen_distance_fast.py $OUT $TMP_DIR $P

    echo "Distance values:"
    head -n5 $TMP_DIR/distance.cfg.txt
    echo "..."
    tail -n5 $TMP_DIR/distance.cfg.txt

    # Instrument the program
    echo "Instrumenting the program"
    cd "$TARGET/repo"

    export CFLAGS="$COPY_CFLAGS -distance=$TMP_DIR/distance.cfg.txt"
    export CXXFLAGS="$COPY_CXXFLAGS -distance=$TMP_DIR/distance.cfg.txt"
    export LIBS="$LIBS $OUT/afl_driver.a -lstdc++"

    "$TARGET/build.sh"

    echo "The second pass of target build is done"

    echo "Instrumentation is done, have a nice day, yay!"
)
