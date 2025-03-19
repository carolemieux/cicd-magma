#!/bin/bash

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

# curl "https://www.sqlite.org/src/tarball/sqlite.tar.gz?r=8c432642572c8c4b" \
#   -o "$OUT/sqlite.tar.gz" && \
# mkdir -p "$TARGET/repo" && \
# tar -C "$TARGET/repo" --strip-components=1 -xzf "$OUT/sqlite.tar.gz"

git clone --no-checkout https://github.com/cc-21/sqlite3.git \
    "$TARGET/repo"
git -C "$TARGET/repo" checkout 552b8380f7ca1f0ff381ecabb479a48ba18f19a5
