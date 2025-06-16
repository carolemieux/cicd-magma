# Corpus Minimization

## libpng
```
"$FUZZER/repo/afl-cmin" -i $SEED/$PROGRAM/0/findings/default/queue -o “$OUT/$PROGRAM_minimized” -- ./libpng_read_fuzzer @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[-] Error: no instrumentation output detected (perhaps crash or timeout).
root@1834d9498dc9:/magma_out/afl# 
```

## libsndfile
```
"$FUZZER/repo/afl-cmin" -i $SEED/$PROGRAM/0/findings/default/queue -o "$OUT/sndfile_fuzzer_mini" -- ./sndfile_fuzzer @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[+] OK, 82 tuples recorded.
[*] Obtaining traces for 6216 input files in '/magma/targets/libsndfile/corpus/seed/sndfile_fuzzer/0/findings/default/queue'.
    Processing 6216 files (forkserver mode)...
[*] Processing traces for input files in '/magma/targets/libsndfile/corpus/seed/sndfile_fuzzer/0/findings/default/queue'.
    Processing file 6216/6216
    Processing tuple 9967/9967 with count 6088...
[+] Found 9967 unique tuples across 6216 files.
[+] Narrowed down to 1787 files, saved in '/magma_out/sndfile_fuzzer_mini'.
```

## libtiff 
```
"$FUZZER/repo/afl-cmin" -i $SEED/$PROGRAM/0/findings/default/queue -o "$OUT/tiff_read_rgba_fuzzer_mini" -- ./tiff_read_rgba_fuzzer @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[-] Error: no instrumentation output detected (perhaps crash or timeout).
```

## libxml2
```
"$FUZZER/repo/afl-cmin" -i $SEED/libxml2_xml_read_memory_fuzzer/0/findings/default/queue -o "$OUT/libxml2_xml_read_memory_fuzzer_mini" -- ./libxml2_xml_read_memory_fuzzer @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...


"$FUZZER/repo/afl-cmin" -i $SEED/libxml2_xml_reader_for_file_fuzzer/0/findings/default/queue -o "$OUT/libxml2_xml_reader_for_file_fuzzer_mini" -- ./libxml2_xml_reader_for_file_fuzzer @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[-] Error: no instrumentation output detected (perhaps crash or timeout).
```

## openssl
```
"$FUZZER/repo/afl-cmin" -i $SEED/asn1/0/findings/default/queue -o "$OUT/asn1_mini" -- ./asn1 @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[+] OK, 989 tuples recorded.
[*] Obtaining traces for 7605 input files in '/magma/targets/openssl/corpus/seed/asn1/0/findings/default/queue'.
    Processing 7605 files (forkserver mode)...
[*] Processing traces for input files in '/magma/targets/openssl/corpus/seed/asn1/0/findings/default/queue'.
    Processing file 7605/7605
    Processing tuple 48795/48795 with count 7477...
[+] Found 48795 unique tuples across 7605 files.
[+] Narrowed down to 2472 files, saved in '/magma_out/asn1_mini'.


"$FUZZER/repo/afl-cmin" -i $SEED/asn1parse/0/findings/default/queue -o "$OUT/asn1parse_mini" -- ./asn1parse @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[+] OK, 443 tuples recorded.
[*] Obtaining traces for 1289 input files in '/magma/targets/openssl/corpus/seed/asn1parse/0/findings/default/queue'.
    Processing 1289 files (forkserver mode)...
[*] Processing traces for input files in '/magma/targets/openssl/corpus/seed/asn1parse/0/findings/default/queue'.
    Processing file 1289/1289
    Processing tuple 5466/5466 with count 1188...
[+] Found 5466 unique tuples across 1289 files.
[+] Narrowed down to 400 files, saved in '/magma_out/asn1parse_mini'.


"$FUZZER/repo/afl-cmin" -i $SEED/bignum/0/findings/default/queue -o "$OUT/bignum_mini" -- ./bignum @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[+] OK, 433 tuples recorded.
[*] Obtaining traces for 1474 input files in '/magma/targets/openssl/corpus/seed/bignum/0/findings/default/queue'.
    Processing 1474 files (forkserver mode)...
[*] Processing traces for input files in '/magma/targets/openssl/corpus/seed/bignum/0/findings/default/queue'.
    Processing file 1474/1474
    Processing tuple 12458/12458 with count 1344...
[+] Found 12458 unique tuples across 1474 files.
[+] Narrowed down to 366 files, saved in '/magma_out/bignum_mini'.


"$FUZZER/repo/afl-cmin" -i $SEED/client/0/findings/default/queue -o "$OUT/client_mini" -- ./client @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[+] OK, 1001 tuples recorded.
[*] Obtaining traces for 5313 input files in '/magma/targets/openssl/corpus/seed/client/0/findings/default/queue'.
    Processing 5313 files (forkserver mode)...
[!] Exit code 1 != 0 received from afl-showmap, terminating...


"$FUZZER/repo/afl-cmin" -i $SEED/server/0/findings/default/queue -o "$OUT/server_mini" -- ./server @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[+] OK, 1001 tuples recorded.
[*] Obtaining traces for 5564 input files in '/magma/targets/openssl/corpus/seed/server/0/findings/default/queue'.
    Processing 5564 files (forkserver mode)...
[*] Processing traces for input files in '/magma/targets/openssl/corpus/seed/server/0/findings/default/queue'.
    Processing file 5564/5564
    Processing tuple 32648/32648 with count 5432...
[+] Found 32648 unique tuples across 5564 files.
[+] Narrowed down to 1562 files, saved in '/magma_out/server_mini'.


"$FUZZER/repo/afl-cmin" -i $SEED/x509/0/findings/default/queue -o "$OUT/x509_mini" -- ./x509 @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[+] OK, 727 tuples recorded.
[*] Obtaining traces for 6085 input files in '/magma/targets/openssl/corpus/seed/x509/0/findings/default/queue'.
    Processing 6085 files (forkserver mode)...
[*] Processing traces for input files in '/magma/targets/openssl/corpus/seed/x509/0/findings/default/queue'.
    Processing file 6085/6085
    Processing tuple 29288/29288 with count 5957...
[+] Found 29288 unique tuples across 6085 files.
[+] Narrowed down to 1937 files, saved in '/magma_out/x509_mini'.
```

## php
```
"$FUZZER/repo/afl-cmin" -i $SEED/exif/0/findings/default/queue -o "$OUT/exif_mini" -- ./exif @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[+] OK, 2095 tuples recorded.
[*] Obtaining traces for 3229 input files in '/magma/targets/php/corpus/seed/exif/0/findings/default/queue'.
    Processing 3229 files (forkserver mode)...
[*] Processing traces for input files in '/magma/targets/php/corpus/seed/exif/0/findings/default/queue'.
    Processing file 3229/3229
    Processing tuple 10530/10530 with count 3101...
[+] Found 10530 unique tuples across 3229 files.
[+] Narrowed down to 824 files, saved in '/magma_out/exif_mini'.


"$FUZZER/repo/afl-cmin" -i $SEED/json/0/findings/default/queue -o "$OUT/json_mini" -- ./json @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[+] OK, 2095 tuples recorded.
[*] Obtaining traces for 3155 input files in '/magma/targets/php/corpus/seed/json/0/findings/default/queue'.
    Processing 3155 files (forkserver mode)...
[*] Processing traces for input files in '/magma/targets/php/corpus/seed/json/0/findings/default/queue'.
    Processing file 3155/3155
    Processing tuple 7476/7476 with count 3027...
[+] Found 7476 unique tuples across 3155 files.
[+] Narrowed down to 676 files, saved in '/magma_out/json_mini'.


"$FUZZER/repo/afl-cmin" -i $SEED/unserialize/0/findings/default/queue -o "$OUT/unserialize_mini" -- ./unserialize @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[+] OK, 2095 tuples recorded.
[*] Obtaining traces for 2064 input files in '/magma/targets/php/corpus/seed/unserialize/0/findings/default/queue'.
    Processing 2064 files (forkserver mode)...
[*] Processing traces for input files in '/magma/targets/php/corpus/seed/unserialize/0/findings/default/queue'.
    Processing file 2064/2064
    Processing tuple 8494/8494 with count 1936...
[+] Found 8494 unique tuples across 2064 files.
[+] Narrowed down to 467 files, saved in '/magma_out/unserialize_mini'.


"$FUZZER/repo/afl-cmin" -i $SEED/parser/0/findings/default/queue -o "$OUT/parser_mini" -- ./parser @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[+] OK, 2131 tuples recorded.
[*] Obtaining traces for 28468 input files in '/magma/targets/php/corpus/seed/parser/0/findings/default/queue'.
    Processing 28468 files (forkserver mode)...
[*] Processing traces for input files in '/magma/targets/php/corpus/seed/parser/0/findings/default/queue'.
    Processing file 28468/28468
    Processing tuple 52185/52185 with count 28340...
[+] Found 52185 unique tuples across 28468 files.
[+] Narrowed down to 5870 files, saved in '/magma_out/parser_mini'.
```

## poppler
```
"$FUZZER/repo/afl-cmin" -i $SEED/pdf_fuzzer/0/findings/default/queue -o "$OUT/poppler/pdf_fuzzer_mini" -- ./pdf_fuzzer @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[+] OK, 42 tuples recorded.
[*] Obtaining traces for 27285 input files in '/magma/targets/poppler/corpus/seed/pdf_fuzzer/0/findings/default/queue'.
    Processing 27285 files (forkserver mode)...
[*] Processing traces for input files in '/magma/targets/poppler/corpus/seed/pdf_fuzzer/0/findings/default/queue'.
    Processing file 27285/27285
    Processing tuple 7068/117660 with count 2...munmap_chunk(): invalid pointer
Aborted (core dumped)
```


## sqlite3
```
"$FUZZER/repo/afl-cmin" -i $SEED/sqlite3_fuzz/0/findings/default/queue -o "$OUT/sqlite3_fuzz_mini" -- ./sqlite3_fuzz @@
corpus minimization tool for afl++ (awk version)

[*] Testing the target binary...
[-] Error: no instrumentation output detected (perhaps crash or timeout).
```
