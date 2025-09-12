#!/usr/bin/env python3

import argparse
from collections import defaultdict
import csv
import errno
import json
import logging
from multiprocessing import Pool
import os
import shutil
import subprocess
import sys
from tempfile import mkdtemp

import pandas as pd

ddr = lambda: defaultdict(ddr)

def parse_args():
    parser = argparse.ArgumentParser(description=(
        "Collects exec info from the experiment workdir and outputs relevant."
    ))
    parser.add_argument("--workers",
                        default=4,
                        help="The number of concurrent processes to launch.")
    parser.add_argument("workdir",
                        help="The path to the Captain tool output workdir.")
    parser.add_argument("outfile",
                        default="-",
                        help="The file to which the output will be written, or - for stdout.")
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help=("Controls the verbosity of messages. "
                              "-v prints info. -vv prints debug. Default: warnings and higher.")
                        )
    return parser.parse_args()

def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        num_sep_this = root.count(os.path.sep)
        yield root, dirs, files, (num_sep_this - num_sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]

def path_split_last(path, n):
    sp = []
    for _ in range(n):
        path, tmp = os.path.split(path)
        sp = [tmp] + sp
    return (path, *sp)

def find_campaigns(workdir):
    ar_dir = os.path.join(workdir, "ar")
    for root, dirs, _, level in walklevel(ar_dir, 3):
        if level == 3:
            for run in dirs:
                # `run` directories always have integer-only names
                if not run.isdigit():
                    logging.warning((
                        "Detected invalid workdir hierarchy! Make sure to point "
                        "the script to the root of the original workdir."
                    ))
                path = os.path.join(root, run)
                yield path

def ensure_dir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def clear_dir(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.exception('Failed to delete %s. Reason: %s', file_path, e)

def extract_fuzzer_stats_and_plot_data(tarball, dest):
    clear_dir(dest)
    # get the path to fuzzer stats/plot_data inside the tarball
    fuzzer_stats = subprocess.check_output(f'tar -tf "{tarball}" | grep "fuzzer_stats"', shell=True)
    plot_data = subprocess.check_output(f'tar -tf "{tarball}" | grep "plot_data"', shell=True)
    fuzzer_stats = fuzzer_stats.decode().rstrip()
    plot_data = plot_data.decode().rstrip()
    # strip all path components until the fuzzer_stats/plot_data files
    ccount = len(fuzzer_stats.split("/")) - 1
    assert (ccount == (len(plot_data.split("/")) - 1))
    os.system(f'tar -xf "{tarball}" --strip-components={ccount} -C "{dest}" {fuzzer_stats} {plot_data}')

def get_fuzzer_stats_and_plot_data(dumpdir, path):
    # Fuzzer stats first
    start_time = None
    last_update = None
    run_time = None

    def get_num_from_line(line):
        """
        For a line of format 'thing : time', gets `time` out as an int
        """
        _, time_raw = line.split(":")
        time_raw = time_raw.strip()
        return int(time_raw)

    with open(os.path.join(dumpdir, "fuzzer_stats"), "r") as f:
            for line in f:
                if "start_time" in line:
                    start_time = get_num_from_line(line)
                if "last_update" in line:
                    last_update = get_num_from_line(line)
                if "run_time" in line:
                    run_time = get_num_from_line(line)

    if run_time is not None:
        # aflpp-style, no need for shenanigans
        return "runtime is (aflpp-style) {run_time}"

    plot_data_start_time = None
    cur_time = None
    plot_data_end_time = None
    with open(os.path.join(dumpdir, "plot_data"), "r") as f:
        for line in f:
            if line.startswith("#"):
                start = True
                continue
            if start:
                plot_data_start_time = line.split(',')[0]
                start = False
            cur_time = line.split(',')[0]
        plot_data_end_time = cur_time

    if plot_data_start_time is None:
        return "plot data empty, runtime 0"

    return f"runtime is (afl-style) {last_update - plot_data_start_time}"




def process_one_campaign(path):
    logging.info("Processing %s", path)
    _, fuzzer, target, program, run = path_split_last(path, 4)

    tarball = os.path.join(path, "ball.tar")
    istarball = False
    if os.path.isfile(tarball):
        istarball = True
        dumpdir = mkdtemp(dir=tmpdir)
        logging.debug("Campaign is tarballed. Extracting to %s", dumpdir)
        extract_fuzzer_stats_and_plot_data(tarball, dumpdir)
    else:
        #dumpdir should be the path that includes plot_data and fuzzer_stats;
        # differs for AFL-style vs AFLPP-style
        fuzzer_stats_path = subprocess.check_output(f'find {path} -name "fuzzer_stats"', shell=True)
        fuzzer_stats_dir = os.path.dirname(fuzzer_stats_path.decode().rstrip())
        plot_data_path = subprocess.check_output(f'find {path} -name "plot_data"', shell=True)
        plot_data_dir = os.path.dirname(plot_data_path.decode().rstrip())
        assert (fuzzer_stats_dir == plot_data_dir)
        dumpdir = fuzzer_stats_dir

    dumpinfo = ""
    try:
        info = get_fuzzer_stats_and_plot_data(dumpdir, path)
    except Exception as ex:
        name = f"{fuzzer}/{target}/{program}/{run}"
        logging.exception("Encountered exception when processing %s. Details: "
                          "%s", name, ex)
    finally:
        if istarball:
            clear_dir(dumpdir)
            os.rmdir(dumpdir)
    return fuzzer, target, program, run, info

def collect_experiment_data(workdir, workers=0):
    def init(*args):
        global tmpdir
        tmpdir, = tuple(args)

    experiment = ddr()
    tmpdir = os.path.join(workdir, "tmp")
    ensure_dir(tmpdir)

    for path in find_campaigns(workdir):
        print(path)
        fuzzer, target, program, run, info = process_one_campaign(path)
        print(info)
    # with Pool(processes=workers, initializer=init, initargs=(tmpdir,)) as pool:
    #     results = pool.starmap(process_one_campaign,
    #                            ((path,) for path in find_campaigns(workdir))
    #                            )
    #     for fuzzer, target, program, run, df in results:
    #         if df is not None:
    #             experiment[fuzzer][target][program][run] = df
    #         else:
    #             # TODO add an empty df so that the run is accounted for
    #             name = f"{fuzzer}/{target}/{program}/{run}"
    #             logging.warning("%s has been omitted!", name)
    #return experiment


def configure_verbosity(level):
    mapping = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    # will raise exception when level is invalid
    numeric_level = mapping[level]
    logging.basicConfig(level=numeric_level)

def main():
    args = parse_args()
    configure_verbosity(args.verbose)
    collect_experiment_data(args.workdir, int(args.workers))
    # summary = get_experiment_summary(experiment)
    #
    # output = {
    #     'results': summary,
    #     # TODO add configuration options and other experiment parameters
    # }
    #
    # data = json.dumps(output).encode()
    # if args.outfile == "-":
    #     sys.stdout.buffer.write(data)
    # else:
    #     with open(args.outfile, "wb") as f:
    #         f.write(data)

if __name__ == '__main__':
    main()
