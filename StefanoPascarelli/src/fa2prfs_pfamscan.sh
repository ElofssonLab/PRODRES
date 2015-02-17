#!/bin/bash

set -e

if (( $# < 1 )); then
    echo "Usage: $0 <fasta file>";
    exit 1;
fi
tmpdir=$1;
infile_path=${tmpdir}query;


#if [[ -s ${infile_path}.prf ]]; then
#    echo "$0: Found file '${infile_path}.mtx', skipping BLAST-run";
#    exit ;
#else
#    echo "No blast result found for ${infile_path}";
#fi


## PFAMSCAN DATABASE CREATION ##

#echo "python pfam_scan_to_profile.py ${infile_path}.fa $tmpdir/"

python pfam_scan_to_profile.py ${infile_path}.fa $tmpdir/
#exit;


# JACKHMMER
python jackbigs.py ${infile_path}.fa $tmpdir/


# Result comparison

python parsejackcompare.py $tmpdir 
