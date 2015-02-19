#!/bin/bash

set -e

if (( $# < 2 )); then
    echo "Usage: $0 <fasta file> <pfamDB path>";
    exit 1;
fi
tmpdir=$1;
infile_path=${tmpdir}query;
dbpath=$2;
pscan_e_val=$3;
clan_overlap=$4;
#if [[ -s ${infile_path}.prf ]]; then
#    echo "$0: Found file '${infile_path}.mtx', skipping BLAST-run";
#    exit ;
#else
#    echo "No blast result found for ${infile_path}";
#fi


## PFAMSCAN DATABASE CREATION ##

#echo "python pfam_scan_to_profile.py ${infile_path}.fa $tmpdir/"
python pfam_scan_to_profile.py ${infile_path}.fa $tmpdir $dbpath $pscan_e_val $clan_overlap/
#exit;


# JACKHMMER
python jackbigs.py ${infile_path}.fa $tmpdir $dbpath/


# Result comparison

python parsejackcompare.py $tmpdir 
