#!/usr/bin/env python
"""
remapper.py
Kyle McChesney

Unoffical script for working with One Codex results files

"""

import logging, argparse, os
from one_codex_result import OneCodexResult


# this outside of main ??

# loggin
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s {%(levelname)s}: %(message)s')

# file log
file_handler = logging.FileHandler("remapper.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# console log
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

# set it all up
log.addHandler(file_handler)
log.addHandler(stream_handler)

def main():
    
    parser = argparse.ArgumentParser(
        description = (" Select a subset of One Codex TSV hits, and recover the actual reads from the fastq file which belong to the headers ")
    )

    # args
    parser.add_argument("--tsv", help="Fullpath to the One Codex results file", required=True)
    parser.add_argument("--fastq", help="Fullpath to the original FASTQ file which was uploaded", required=True)
    parser.add_argument("--threads", help="Number of worker threads for processing results", default=1)
    parser.add_argument("--contains-ids", help="Conditionally select results which contain a given TAX ID", nargs='+')
    parser.add_argument("--or", help="treats the ids from contains-ids as OR", default=False)
    parser.add_argument("--min-matched", help="Percentage of the read which matched a single tax ID", type=float)

    args = parser.parse_args()
    log.info(" remapper running with TSV: %s and FASTQ: %s", args.tsv, args.fastq)

    # read the results
    log.info(" reading in One Codex results...")
    results = read_results(args.tsv)
    log.info(" Read in %i results", len(results))


def read_results(tsv_file):
    
    result_objs = []
    
    # make sure the file exists
    if not os.path.isfile(tsv_file):
        print "NOT A FILE"
        log.warn("%s is not a file!", tsv_file)
        raise SystemExit

    # open it
    result = None
    with open(tsv_file, "r") as tsv:

        # skip the header
        next(tsv)

        # iter over all results
        for line in tsv:
            header, tax, hits, read_length, chain = line.split("\t")
            chain = chain.rstrip()
            result = OneCodexResult(header, int(tax), int(hits), int(read_length), chain)
            result_objs.append(result)

    return result_objs

# pass the conditions in as a list of functions on results
#def search(results, conditions):

if __name__ == "__main__":
    main()