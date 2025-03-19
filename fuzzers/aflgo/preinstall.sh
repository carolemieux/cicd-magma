#!/bin/bash
set -e

apt-get update
LLVM_DEP_PACKAGES="build-essential make cmake ninja-build git binutils-gold binutils-dev curl wget python3"
apt-get install -y $LLVM_DEP_PACKAGES

apt-get update
apt-get install -y python3-dev python3-pip pkg-config autoconf automake libtool-bin gawk libboost-all-dev

python3 -m pip install --upgrade pip
# See https://networkx.org/documentation/stable/release/index.html
case `python3 -c 'import sys; print(sys.version_info[:][1])'` in
    [01])
        python3 -m pip install 'networkx<1.9';;
    2)
        python3 -m pip install 'networkx<1.11';;
    3)
        python3 -m pip install 'networkx<2.0';;
    4)
        python3 -m pip install 'networkx<2.2';;
    5)
        python3 -m pip install 'networkx<2.5';;
    6)
        python3 -m pip install 'networkx<2.6';;
    7)
        python3 -m pip install 'networkx<2.7';;
    8)
        python3 -m pip install 'networkx<=3.1';;
    *)
        python3 -m pip install networkx;;
esac
python3 -m pip install pydot pydotplus
