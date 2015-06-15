#!/usr/bin/env python
"""
remapper.py
Kyle McChesney

Unoffical script for working with One Codex results files

"""

import logging, argparse, os, itertools
import pp
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
    parser.add_argument("--threads", help="Number of worker threads for processing results", default=1, type=int)
    parser.add_argument("--contains-ids", help="Conditionally select results which contain a given TAX ID", nargs='+', type=int)
    parser.add_argument("--is-or", help="treats the ids from contains-ids as OR", default=False)
    parser.add_argument("--min-matched", help="Percentage of the read which matched given TAX id(s)", type=float, default=1.0)

    args = parser.parse_args()

    log.info(" remapper running with TSV: %s and FASTQ: %s", args.tsv, args.fastq)

    # read the results
    log.info(" reading in One Codex results...")
    results = read_results(args.tsv, args.contains_ids, args.is_or)
    log.info(" Read in %i results", len(results))

    # split the results and pass off to workers
    chunks = split_results(results, args.threads)

    # set up pp stuff
    ppservers = ()
    job_server = pp.Server(args.threads, ppservers=ppservers)
    
    # start up the jobs
    jobs = []
    for chunk in chunks:
        jobs.append(job_server.submit(search, (chunk, args.contains_ids, args.is_or, args.min_matched)))

    job_server.wait()

    matching = []
    for job in jobs:
        for result in job():
            matching.append(result.header)

    log.info("Found %i results which matched", len(matching))

    fastqs = find_fastqs(matching, args.fastq)

    # write the result
    with open("remapper-results.fastq", "w") as out:
        for line in fastqs:
            out.write(line)
    
def split_results(results, count):
    
    # if there is a remainder, we redistribute those pieces back into the rest 
    remainder = len(results) % count
    unequal = None
    if remainder != 0:

        # grab the unequal piece and take it out
        unequal = results[0:remainder]

        # remove it from the main list
        results = results[:-remainder]

    # calc the size of the equal sized lists
    equal_length = len(results) / count

    chunks = [results[i:i+equal_length] for i in range(0,count) ]

    # front load them
    if unequal is not None:
        i = 0
        for element in unequal:
            chunks[i].append(element)
            i += 1

    return chunks

def read_results(tsv_file, ids, is_or):
    
    result_objs = []
    
    # make sure the file exists
    if not os.path.isfile(tsv_file):
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

            if not precheck_result(chain, ids, is_or):
                continue
                
            result = OneCodexResult(header, int(tax), int(hits), int(read_length), chain)
            result_objs.append(result)

    return result_objs

# pass the conditions in as a list of functions on results
# contains_ids = []   - list of IDS we are looking for in the kmer chain
# or = Boolean        - if our ids is more than one, then the matches can either be AND (matches for all ids) or OR (at least one)
# min-matched = float - percentage of the total read which must have been matched
def search(results, ids, is_or, cutoff):
    
    # store matches in here
    matching_results = []

    # iterate through all the chunks
    for result in results:
        
        # create data structure to store kmer stats
        # dict{id} --> hit count
        stats = { id: 0 for id in ids}

        # iterate over the expanded k-mer chain
        for base in result.kmer_chain:
            if base in stats:
                stats[base] += 1

        # check if conditions are met
        all_met = True
        one_met = False

        for id in ids:
            if stats[id]/result.read_length >= cutoff:
                one_met = True
            else:
                all_met = False

        if all_met or (one_met and is_or):
            matching_results.append(result)

    return matching_results


def find_fastqs(headers, fastq_file):

    fastqs = []
    
    # make sure the file exists
    if not os.path.isfile(fastq_file):
        log.warn("%s is not a file!", fastq_file)
        raise SystemExit

    # read it
    with open(fastq_file, "r") as fastq:

        for line in fastq:

            if line.rstrip() in headers:
                fastqs.append(line)
                fastqs.append(next(fastq, None))
                fastqs.append(next(fastq, None))
                fastqs.append(next(fastq, None))
            
            else:
                # skip to the next header
                next(fastq, None)
                next(fastq, None)
                next(fastq, None)

    return fastqs


def precheck_result(chain, tax_ids, is_or):

    contains_one = False
    contains_all = True
    for id in tax_ids:
        if "{}:".format(id) in chain:
            contains_one = True
        else:
            contains_all = False

    return contains_all or contains_one and is_or

if __name__ == "__main__":
    main()