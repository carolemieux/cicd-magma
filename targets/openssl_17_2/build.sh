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

# build the libpng library
cd "$TARGET/repo"

#CONFIGURE_FLAGS=""
#if [[ $CFLAGS = *sanitize=memory* ]]; then
CONFIGURE_FLAGS="no-asm"
#fi

# the config script supports env var LDLIBS instead of LIBS
export LDLIBS="$LIBS $FUZZER_LIB"

./config --debug enable-fuzz-libfuzzer enable-fuzz-afl disable-tests -DPEDANTIC \
    -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION no-shared no-module \
    enable-tls1_3 enable-rc5 enable-md2 enable-ec_nistp_64_gcc_128 enable-ssl3 \
    enable-ssl3-method enable-nextprotoneg enable-weak-ssl-ciphers \
    $CFLAGS -fno-sanitize=alignment $CONFIGURE_FLAGS

echo "Check the flags"
grep -w "CFLAGS=" Makefile
grep -w "CXXFLAGS=" Makefile

replacedCFLAG=$(grep -w "CFLAGS=" Makefile | awk '{for (i=1;i<=NF;i++) if (!a[$i]++) printf("%s%s",$i,FS)}{printf("\n")}')
replacedCXXFLAG=$(grep -w "CXXFLAGS=" Makefile | awk '{for (i=1;i<=NF;i++) if (!a[$i]++) printf("%s%s",$i,FS)}{printf("\n")}')
replacedCFLAG=$(echo $replacedCFLAG | sed s/" -include"//)
replacedCXXFLAG=$(echo $replacedCXXFLAG | sed s/" -include"//)

sed -i '/CFLAGS=-include/c\'"$replacedCFLAG"'' Makefile
sed -i '/CXXFLAGS=-include/c\'"$replacedCXXFLAG"'' Makefile

echo "Should be correct now"
grep -w "CFLAGS=" Makefile
grep -w "CXXFLAGS=" Makefile

make -j$(nproc) clean
make -j$(nproc) LDCMD="$CXX $CXXFLAGS"

fuzzers=$(find fuzz -executable -type f '!' -name \*.py '!' -name \*-test '!' -name \*.pl)
for f in $fuzzers; do
    fuzzer=$(basename $f)
    cp $f "$OUT/"
    if [ -f $f.0.0.*.bc ]; then 
        cp $f.0.0.*.bc "$OUT/"
    fi
done
