#!/bin/bash
set -e

apt-get update && apt-get install -y \
        build-essential \
        python3-dev \
        python3-setuptools \
        automake \
        git \
        flex \
        bison \
        libglib2.0-dev \
        libpixman-1-dev \
        cargo \
        libgtk-3-dev \
        vim \
        libc++-dev \
        libc++abi-dev

# for QEMU mode
apt-get install -y \
        ninja-build \
        gcc-$(gcc --version|head -n1|sed 's/\..*//'|sed 's/.* //')-plugin-dev \
        libstdc++-$(gcc --version|head -n1|sed 's/\..*//'|sed 's/.* //')-dev

apt-get install -y git gcc g++ make cmake wget \
        libgmp-dev libmpfr-dev texinfo bison python3

apt-get install -y libboost-all-dev libjsoncpp-dev libgraphviz-dev \
    pkg-config libglib2.0-dev findutils

apt-get install -y lsb-release wget software-properties-common python3-pip

# these two packages are automatically installed, libpcap will consider libnl
# installed and try to link with libnl-genl-3-dev, which is not installed.
# Simply remove these packages
apt-get remove libnl-3-200 libnl-3-dev -y

pip3 install --upgrade pip
pip3 install networkx pydot cmake
