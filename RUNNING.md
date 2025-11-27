# Running New Experiments

This document describes how to run new experiments in the CI/CD Magma Simulation.

Each experiment is a run of a particular fuzzer on a particular target (benchmark). The target (benchmark) is where 
any target lines (for directed fuzzers) can be specified. 

## Target (Benchmark) Structure

To run an experiment, we must have a benchmark to run on. 

In the TOSEM paper, we consider 50 benchmarks consisting of a project, patch, and fuzz driver pair.  For ease of use, we
create separate targets for each of these 50 benchmarks.

Benchmark details for `BENCH_NAME` are found in a folder `targets/BENCH_NAME`. In this folder, configuration is set in  
the `configrc` file, `targets/BENCH_NAME/configrc`.

If you want to use the benchmarks from our TOSEM paper, you
can directly use these configurations. If you would like to create new configurations, read on.

### Target configrc details

A regular magma target configrc file sets the `PROGRAMS` environment variable to all the fuzz drivers to fuzz, and any 
project-specific environment variables. For openssl, Magma's configrc contains simply:

```bash
PROGRAMS=(asn1 asn1parse bignum server client x509)
```

For our benchmark `openssl_20_4`, which inserts the SSL020 patch and uses the fuzz driver `server`, the config file is:

```bash
PROGRAMS=(server)

PATCHES="SSL020"
AUTOMATIC=1
COMMIT_FILES=(ssl/t1_lib.c)
```

The `PATCHES` variable stores the patch to be inserted. Only this patch will be inserted, rather than the Magma 
default of inserting all patches.

`AUTOMATIC` indicates that the directed fuzzers will try to automatically derive the target file from this patch. This 
requires the base project to be a git repository. If one would like to specify the target file manually, as we did in 
our sensitivity experiments, to measure the bloat in commits, this line should be removed. The directed fuzzing targets 
should be manually specified in a file with name PATCH (in this case, SSL020) in the subdirectory `fuzzers/DIRECTED_FUZZER/targets`. 
For example, `sqlite3` is not a git repository, so the automatic target file generation does not work for it. Thus, 
`fuzzers/aflgo/targets` contains files for `SQL002`, `SQL018`, `SQL020`.

Finally, `COMMIT_FILES` is an array of the files modified in the patch(es) specified in `PATCHES`. 
This last variable is used by the coverage analysis pipeline to gather coverage of the files modified in the patch 
(i.e., running `llvm\_cov`); it need not be set for running the other fuzzers.

### Running Benchmarks with Custom Target Lines (e.g., Sensitivity Experiments)

The `AUTOMATIC=1` line will automatically generate target lines for the given patch to pass to a directed fuzzer.

To use custom target lines, REMOVE/COMMENT-OUT this line from the configrc, e.g.:

```bash
PROGRAMS=(server)

PATCHES="SSL020"
#AUTOMATIC=1
COMMIT_FILES=(ssl/t1_lib.c)
```
and ensure that the fuzzing targets (a file where each line is `filename:lineno`) are specified in `fuzzers/DIRECTED_FUZZER/targets/PATCH`
for the patches of interest (i.e., `SSL020` above) and the `DIRECTED_FUZZER` of interest (e.g., aflgo/aflgoexp, ffd, windranger).

For our sensitivity experiments, comment out `AUTOMATIC=1` as above for each benchmark in the sensitivity experiment, 
and replace the contents of the `targets` directory for each directed fuzzer with the contents of `targets_for_sensitivity`
for each patch of interest. Then, running the experiments on this benchmark will pass these adjusted target files to the
directed fuzzers.

## Running Experiments 

To run experiments, go to the `tools/captain` folder and run: 

```
$ ./run.sh
```

This will run experiments according to the specification in `tools/captain/captainrc`.

Most of the `captainrc` variables are identical to those in Magma; refer to the comments in the `captainrc` or the
[Magma documentation](https://hexhive.epfl.ch/magma/docs/config.html) for more detail. 

Unique to `cicd-magma` is the manual specification of corpus directories. This is so that we could run our experiments 
with a custom saturated corpus. The corpus to use for each `fuzzer`, `target` pair must be specified in the variable
`fuzzer_target_CORPUS`. The corpus directory is relative to the top-level `seed` directory.

The `captainrc_for_experiments` contains example captainrc files for each fuzzer, which specifes all these CORPUS
variables. The default `captainrc` in the repository is the one to run `aflgoexp` (AFLGo with time-to-exploit set to 0m).

The `WORKDIR` variable is where results will be stored. This `WORKDIR` is the equivalent to `main-experiment-raw-data/fuzzer`
or `sensitivity-experiment-raw-data/fuzzer` in our raw results distributed on Zenodo. 



