#  This file takes a file created by MAGMA's exp2json, listing times 
#  to reach/trigger bugs, and adds instrumentation time to those values.
#  we remove reached/triggered bugs if the time with instrumentation 
#  is above a threshold.
import sys
import json

CUTOFF=600

# loads instrumentation times and returns
# a dictionary mapping benchmark --> instrumentation time
def load_instrumentation_times(inst_file_name):
    ret = {}
    with open(inst_file_name) as f:
        for line in f:
            benchmark, time = line.strip().split(',')
            if time == '':
                print(f"No time for {benchmark}", file=sys.stderr)
                continue
            time = float(time)
            ret[benchmark]=time
    return ret


# creates a dictionary object with instrumentation times added.
def add_instrumentation_times(json_file_name, inst_dict):
     dict_with_inst = {"results":{}}
     with open(json_file_name, "r") as f:
         data= json.load(f)
         # assume we only have a single technique's results,
         # else we're gonna add the wrong instrumentation times somewhere
         assert len(data["results"]) == 1
         technique_name = next(iter(data["results"]))     
         per_benchmark_results = {}
         for benchmark, fuzzer_results in data["results"][technique_name].items():
             # assume only one fuzz driver per becnhmark
             assert len(fuzzer_results) == 1
             fuzz_driver_name = next(iter(fuzzer_results))
             res_with_inst = {}
             for iteration, results in fuzzer_results[fuzz_driver_name].items():
                 # results should have the key reached and triggered
                 reached_dict = results["reached"]
                 if len(reached_dict) == 0:
                      reached_key = {}
                 else:
                     # only one bug per target
                     assert len(reached_dict) == 1
                     bug_id = next(iter(reached_dict))
                     reached_time = reached_dict[bug_id] + inst_dict[benchmark]
                     if reached_time > CUTOFF:
                         print(f"NOTE: for {benchmark}-{fuzz_driver_name}-{iteration}, reached time is now {reached_time}", file=sys.stderr)
                         reached_key = {}
                     else:
                         reached_key = {bug_id: reached_time}
                 triggered_dict = results["triggered"]
                 if len(triggered_dict) == 0:
                      triggered_key = {}
                 else:
                     # only one bug per target
                     assert len(triggered_dict) == 1
                     bug_id = next(iter(triggered_dict))
                     triggered_time = triggered_dict[bug_id] + inst_dict[benchmark]
                     if triggered_time > CUTOFF:
                         print(f"NOTE: for {benchmark}-{fuzz_driver_name}-{iteration}, triggered time is now {triggered_time}", file=sys.stderr)
                         triggered_key = {}
                     else:
                         triggered_key = {bug_id: triggered_time}
                 res_with_inst[iteration] = {"reached": reached_key, "triggered": triggered_key}
             new_res = {fuzz_driver_name: res_with_inst}
             per_benchmark_results[benchmark] = new_res
         dict_with_inst["results"] = {technique_name:per_benchmark_results}
     return dict_with_inst



def main():
    if len(sys.argv) != 4:
        print(f"Usage: python3 {sys.argv[0]} json-results instrumentation-time-csv results-filename")
        print("adds instrumentation time to MAGMA json results, with cutoff times")
        print("WARNING: assumes the results json is for one technique only, as we")
        print("only take in a single instrumentation time file")
        exit(1)
    json_file_name=sys.argv[1]
    inst_file_name=sys.argv[2]
    inst_dict = load_instrumentation_times(inst_file_name)
    out_dict = add_instrumentation_times(json_file_name, inst_dict)
    outfile = sys.argv[3]
    with open(outfile, 'w') as f:
        json.dump(out_dict,f)


if __name__ == "__main__":
    main()
