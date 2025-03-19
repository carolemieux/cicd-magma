#!/bin/bash

##
# Pre-requirements:
# - env FUZZER: path to fuzzer work dir
##

# git clone --no-checkout https://github.com/rohanpadhye/FuzzFactory.git "$FUZZER/repo"
# git -C "$FUZZER/repo" checkout e02d439572f981d4931cfc88f1dae64ce71cb82d

git clone --no-checkout https://github.com/cc-21/FuzzFactoryDiff.git "$FUZZER/repo"
git -C "$FUZZER/repo" checkout f669cdfd5c53bcd45cc1f0b9d8f66244d961c4db

cp "$FUZZER/src/afl_driver.cpp" "$FUZZER/repo/afl_driver.cpp"
