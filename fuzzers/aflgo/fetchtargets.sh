#!/bin/bash
# Output-> BBTargets.txt
set -e

source $TARGET/configrc

if [[ -z "${AUTOMATIC}" ]]; then
    PATCH="${PATCHES}.patch" #TODO: if PATCHES include more than one patch, it will fail. Fix later
    echo "Fetching BB targets manually"
    cp $FUZZER/targets/${PATCHES} $TMP_DIR/BBtargets.txt
else
    echo "Fetching BB targets automatically"
    cd $TARGET/repo
    # Download commit-analysis tool
    wget https://raw.githubusercontent.com/jay/showlinenum/develop/showlinenum.awk
    chmod +x showlinenum.awk
    mv showlinenum.awk $TMP_DIR

    git diff >> $TMP_DIR/commit.diff
    echo "The diff is:"
    cat $TMP_DIR/commit.diff
    cat $TMP_DIR/commit.diff | $TMP_DIR/showlinenum.awk show_header=0 path=1 | grep -e "\.[ch]:[0-9]*:+" -e "\.cpp:[0-9]*:+" -e "\.cc:[0-9]*:+" | cut -d+ -f1 | rev | cut -c2- | rev > $TMP_DIR/BBtargets.txt
fi
