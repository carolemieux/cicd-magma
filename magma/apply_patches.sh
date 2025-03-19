#!/bin/bash
set -e

##
# Pre-requirements:
# - env TARGET: path to target work dir
##

source $TARGET/configrc

# TODO filter patches by target config.yaml
if [ -d "$TARGET/patches/setup" ]; then 
  find "$TARGET/patches/setup" -name "*.patch" |
    while read patch; do
      echo "Applying $patch for setup"
      patch --verbose -p1 -d "$TARGET/repo" <"$patch"
    done
  pushd $TARGET/repo
  git add .
  popd
fi

if [[ -z "$PATCHES" ]] || [[ "$PATCHES" == "ALL_PATCHES" ]]; then
    echo "Applying all the patches"
    find "$TARGET/patches/bugs" -name "*.patch" | \
    while read patch; do
        echo "Applying $patch" 
        name=${patch##*/}
        name=${name%.patch}
        sed "s/%MAGMA_BUG%/$name/g" "$patch" | patch -p1 -d "$TARGET/repo"
    done
else 
    find "$TARGET/patches/bugs" -name "*.patch" | \
    while read patch; do
        name=${patch##*/}
        name=${name%.patch}
        if [[ "${PATCHES[*]}" == *"$name"* ]]; then 
            echo "Applying $patch" 
            sed "s/%MAGMA_BUG%/$name/g" "$patch" | patch -p1 -d "$TARGET/repo"
        fi
    done
fi
