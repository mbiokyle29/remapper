# remapper
An unoffical program to selectively pick out One Codex results and pull out the FASTQ reads they represent

# installation
```
git clone git@github.com:mbiokyle29/remapper.git
cd remapper
pip install -r requirements.txt
```

# using
```
usage: remapper.py [-h] --tsv TSV --fastq FASTQ [--threads THREADS]
                   [--contains-ids CONTAINS_IDS [CONTAINS_IDS ...]]
                   [--is-or IS_OR] [--min-matched MIN_MATCHED]

Select a subset of One Codex TSV hits, and recover the actual reads from the
fastq file which belong to the headers

optional arguments:
  -h, --help            show this help message and exit
  --tsv TSV             Fullpath to the One Codex results file
  --fastq FASTQ         Fullpath to the original FASTQ file which was uploaded
  --threads THREADS     Number of worker threads for processing results
  --contains-ids CONTAINS_IDS [CONTAINS_IDS ...]
                        Conditionally select results which contain a given TAX
                        ID
  --is-or IS_OR         treats the ids from contains-ids as OR
  --min-matched MIN_MATCHED
                        Percentage of the read which matched given TAX id(s)
```
# examples

## Finding all reads which are 100% matching tax_id 10 (using 10 searching threads)
```
remapper.py --tsv my-results.tsv --fastq my-fastq --threads 10 --contains-ids 10 --min-matched 1
```

## find all reads that are aleast 50% tax_id 10 OR 50% tax_id 20
```
remapper.py --tsv my-results.tsv --fastq my-fastq --threads 10 --contains-ids 10 20 --min-matched .5 --is-or true
```
