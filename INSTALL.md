Ensure docker is installed on your machine before proceeding. 

To run AFL-based fuzzers you must set
```
echo core >/proc/sys/kernel/core_pattern
```
which may require root access.


# Verifying a minimal installation

Copy `tools/captain/captainrc_for_tests/minimal_captainrc` to `tools/captain/captainrc`. This configuration specifes running 1 iteration of `aflgoexp` for 1 minute on the `libpng_4_1` benchmark.

Navigate to `tools/captain/captainrc` and run `./run.sh`.

If things are working correctly, the first messages you should see on stdout are:
```
[<START_TIME>] Obtaining sudo permissions to mount tmpfs
[<START_TIME>] The corpus is libpng/libpng_read_fuzzer
[<START_TIME>] Building magma/aflgoexp/libpng_4_1
```
Then, the artifact will build the fuzzer and fuzz target---this took 9 minutes on our machine. You should then see:
```
[<START_TIME>+<BUILD_TIME>] Starting campaigns for libpng_read_fuzzer 
[<START_TIME>+<BUILD_TIME>] Waiting for jobs to finish
[<START_TIME>+<BUILD_TIME>] Container aflgoexp/libpng_4_1/libpng_read_fuzzer/0 started on CPU 0
[<START_TIME>+<BUILD_TIME>+1m]  Container aflgoexp/libpng_4_1/libpng_read_fuzzer/0 stopped
[<START_TIME>+<BUILD_TIME>+1m]  Obtaining sudo permissions to umount tmpfs
```

If the fuzzer and target built successfully, `./minimal-working-example/log/aflgoexp_libpng_4_1_build.log` should end with:
```
#30 DONE <TIME>s
+ set +x
magma/aflgoexp/libpng_4_1
```

If the fuzzing ran successfully, `./minimal-working-example/log/aflgoexp_libpng_4_1_libpng_read_fuzzer_0_container.log` should contain several lines saying `Attempting dry run with '<filename'>`, and lines with `Fuzzing test case #X (Y total, 0 uniq crashes found)...`
before the line `+++ Testing aborted by user +++`. You may see an error message about `docker rmi`; this is fine. 
