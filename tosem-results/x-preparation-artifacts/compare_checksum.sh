#!/bin/bash

# Sanity check
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <base_path1> <base_path2>"
    exit 1
fi

base_path_before=$1
base_path_after=$2

# List of libraries
libraries=("openssl_11" "openssl_3" "openssl_10" "openssl_16" "openssl_5" "openssl_18" "openssl_12" "php_15" "php_8" "php_2" "php_14" "poppler_20" "poppler_17" "poppler_16" "poppler_6" "poppler_11" "poppler_8" "poppler_7" "sqlite3_7" "sqlite3_15" "sqlite3_12" "sqlite3_4" "sqlite3_10" "sqlite3_18" "sqlite3_16")
#"libpng_7" "libpng_5" "libpng_4" "libpng_1" "libsndfile_1" "libsndfile_2" "libsndfile_4" "libsndfile_5" "libsndfile_6" "libsndfile_7" "libsndfile_10" "libsndfile_13" "libsndfile_14" "libsndfile_20" "libtiff_5" "libtiff_14" "libtiff_13" "libtiff_7" "libtiff_6" "libxml2_8" "libxml2_15" "libxml2_6" "libxml2_7" "libxml2_9" "libxml2_5"
#"openssl_11" "openssl_3" "openssl_10" "openssl_16" "openssl_5" "openssl_18" "openssl_12" "php_15" "php_8" "php_2" "php_14" "poppler_20" "poppler_17" "poppler_16" "poppler_6" "poppler_11" "poppler_8" "poppler_7" "sqlite3_7" "sqlite3_15" "sqlite3_12" "sqlite3_4" "sqlite3_10" "sqlite3_18" "sqlite3_16"
for library in "${libraries[@]}"; do
    checksum_before=($base_path_before/$library/*/0/checksum)
    checksum_after=($base_path_after/$library/*/0/checksum)

    if [[ ${#checksum_before[@]} -ne ${#checksum_after[@]} ]]; then
        echo "The number of files is different."
        exit 1
    fi

    for ((i=0; i<${#checksum_before[@]}; i++)); do

        file_before="${checksum_before[i]}"
        file_after="${checksum_after[i]}"

        if diff -q "$file_before" "$file_after" > /dev/null; then
            target_before=$(echo "$file_before" | awk -F'/' '{print $(NF-3)"/"$(NF-2)}')
            target_after=$(echo "$file_after" | awk -F'/' '{print $(NF-3)"/"$(NF-2)}')
            echo "Files have the same content: $target_before and $target_after"
        fi
    done

done
