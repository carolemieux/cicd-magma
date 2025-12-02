#!/bin/bash

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
# - env TARGET: path to target work dir
# - env OUT: path to directory where artifacts are stored
# - env SHARED: path to directory shared with host (to store results)
# - env PROGRAM: name of program to run (should be found in $OUT)
# - env ARGS: extra arguments to pass to the program
# - env FUZZARGS: extra arguments to pass to the fuzzer
# - env COVERAGE_FUZZER: fuzzer to collect coverage for
##

echo "No fuzzer included. This is just for building an analysis target."
echo "Collecting coverage for fuzzer ${COVERAGE_FUZZER}."

mkdir -p $SHARED/coverage
pushd $FUZZER

if [ ! -d "$SEED/${COVERAGE_FUZZER}/$PROGRAM" ]; then
	echo "$SEED/${COVERAGE_FUZZER}/$PROGRAM does not exist; not collecting coverage"
	popd 
	exit 1
fi

for repdir in "$SEED/${COVERAGE_FUZZER}/$PROGRAM/*"; do 
    i=$(basename $repdir)
    if [ -d $repdir/findings/queue ]; then    #afl-style
    	export CORPUS="$SEED/${COVERAGE_FUZZER}/$PROGRAM/$i/findings/queue"
    	./collect_coverage.sh $i ${COVERAGE_FUZZER}
    elif [ -d $repdir/findings/default/queue ]; then #aflpp-style
    	export CORPUS="$SEED/${COVERAGE_FUZZER}/$PROGRAM/$i/findings/default/queue"
    	./collect_coverage.sh $i ${COVERAGE_FUZZER}
    else
	echo "Could not find queue directory; not collecting coverage"
    fi
done

popd
exit 1
