#!/bin/bash
# set -e
##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
# - env TARGET: path to target work dir
# - env OUT: path to directory where artifacts are stored
# - env SHARED: path to directory shared with host (to store results)
# - env PROGRAM: name of program to run (should be found in $OUT)
# - env ARGS: extra arguments to pass to the program
# - env FUZZARGS: extra arguments to pass to the fuzzer
# - env CORPUS: the path to the corpus of inputs
##

if [ -n "$2" ]; then
    export iter="$1"
    export fuzzer_name="$2"
    echo "iter is set to: $iter"
else
    echo "No argument provided. iter is not set."
fi

pushd $OUT

for file in "$CORPUS"/*; do 
    if [ -f "$file" ]; then 
        export LLVM_PROFILE_FILE="$(basename $file).profraw"
        timeout 10s ./$PROGRAM $FUZZARGS $file
    else 
        echo "File $file does not exist"
    fi 
done

export TARGET_NAME=$(basename $TARGET)

echo "The target corpus is $CORPUS"
echo "The target is $TARGET_NAME"

source "$TARGET/configrc"
COMMIT_PATHS=("${COMMIT_FILES[@]/#/"$TARGET/repo/"}")

echo "The commit files are $COMMIT_FILES"
echo "The commit paths are $COMMIT_PATHS"

echo "Check the number of profdata..."
ls $OUT/*.profraw | wc -l

# must specify the version number of llvm-profdata
echo "Merging profraw files..."
llvm-profdata-14 merge *.profraw -o merged.profdata

echo "Get the total coverage..."
llvm-cov report -instr-profile merged.profdata $PROGRAM > $SHARED/coverage/"$fuzzer_name"_"$TARGET_NAME"_"$PROGRAM"_"$iter"_total_coverage.txt

# echo "Get the coverage of the target file..."
if [[ "$TARGET" == *"sqlite3"* ]]; then
    llvm-cov report -instr-profile merged.profdata $PROGRAM $TARGET/work/sqlite3.c -show-functions > $SHARED/coverage/"$fuzzer_name"_"$TARGET_NAME"_"$PROGRAM"_"$iter"_target_file_coverage.txt
else
    llvm-cov report -instr-profile merged.profdata $PROGRAM ${COMMIT_PATHS[@]} -show-functions > $SHARED/coverage/"$fuzzer_name"_"$TARGET_NAME"_"$PROGRAM"_"$iter"_target_file_coverage.txt
fi

# clean up
rm $OUT/*.prof*

popd
