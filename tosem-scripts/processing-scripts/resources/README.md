This directory contains resources from the processing scripts.

Right now it is only `target_to_fns.csv`, which is a csv where the first element is the name of a benchmark, and the remaining
elements are the functions that contain the targeted code. This is used by `extract_target_coverage_to_csv.sh` in the
parent directory, and needs to be modified if you seek to use our scripts to collect the coverage of functions that contain
targeted code, but for a different set of benchmark. 