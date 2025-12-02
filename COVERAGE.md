# Collecting Coverage

We have a custom "fuzzer", `llvm_cov`, which allows us to procedurally collect coverage from experiment results within
the Magma framework. You will have to touch 3 things to use this coverage collection framework:

1. The `Dockerfile`, to update dependencies and specify the fuzzer to collect coverage for
2. The `seed/` directory to contain experiment corpuses
3. The `captainrc` file to run `llvm_cov`, specify longer timeouts, specify targets, and result directory.

## Docker changes

Copy `Dockerfile_coverage` to `Dockerfile` in the `docker` directory. In the dockerfile, set `COVERAGE_FUZZER` (line 15)
to the fuzzer whose results you are collecting coverage for. By default, it is set to `aflgoexp`. 

## Seed changes

You must also copy the corpuses you want to evaluate corpus of to the place the dockerfile expects. Supposing you have
`RESULTS_BASE` holding the results of your experiments, i.e. containing `ar`, `log`, `poc` folders, you should copy/move
`RESULTS_BASE/ar/COVERAGE_FUZZER` to `seed/COVERAGE_FUZZER`. Thus, `seed/COVERAGE_FUZZER` contains directories of the form:
`BENCHMARK/FUZZ_DRIVER/i` for each iteration `i`. For our coverage collection to work, the results for each iteration 
must be untarred. I.e., you should run `tar -xf ball.tar` in each `BENCHMARK/FUZZ_DRIVER/i` folder. 

To do this systematically; 
```bash
base=$MAGMA_PATH/seed/$COVERAGE_FUZZER

for dir in $base/*/*/*; do
  pushd $dir
  tar -xf ball.tar
  popd
done
```

## Captainrc changes

After the dockerfile and seed directories are setup, you must now setup the captainrc. `[captainrc_coverage_experiment_example](tools/captain/captainrc_for_experiments/captainrc_coverage_experiment_example)`
contains an example. You should adjust the `WORKDIR` to where you want to store the results, and the `TARGETS` to list
all the targets/benchmark you are interested in. 

Note a few things: 
1. You need not specify multiple repetitions for the `llvm_cov` fuzzer; its `collect_coverage.sh` automatically 
discovers iterations and collects coverage for each one separately.
2. You may need to specify a longer timeout if you ended up with a large seed corpus. The captainrc example 
sets this to 24h. However, the container will  exit once coverage is done being collected. 

## Run coverage collection

After all the above is setup, `./run.sh` in the `tools/captain` directory will run the coverage collection. Coverage
results will appear in `$WORKDIR/ar/llvm_cov/TARGET/FUZZ_DRIVER/0/` for each specified target. (`0` if you only run
the coverage script once).

The coverage results will be in the subdirectory `coverage`, and you should see files:
`${COVERAGE_FUZZER}_${TARGET}_${FUZZ_DRIVER}_${FUZZING_ITERATION}_target_file_coverage.txt` and 
`${COVERAGE_FUZZER}_${TARGET}_${FUZZ_DRIVER}_${FUZZING_ITERATION}_total_coverage.txt`. The target files are specified in each
target's configrc (as described in [RUNNING.md](RUNNING.md)).

This `coverage` subdirectory can be used as the `COVERAGE_DIR` for data processing,
as described in the `tosem-scripts` [README.md](tosem-scripts/README.md).

