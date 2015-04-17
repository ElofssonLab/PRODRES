#!/bin/bash

set -e

if (( $# < 4 )); then
    echo "Usage: $0 <fasta file> <pfamDB path> <pscan eval> <clan overlap> <flag>";
    exit 1;
fi
tmpdir=$1;
infile_path=${tmpdir}query;
dbpath=$2;
pscan_e_val=$3;
clan_overlap=$4;
flag=$5
#if [[ -s ${infile_path}.prf ]]; then
#    echo "$0: Found file '${infile_path}.mtx', skipping BLAST-run";
#    exit ;
#else
#    echo "No blast result found for ${infile_path}";
#fi
echo $flag ;
# PFAMSCAN DATABASE CREATION ##
if (($flag !='0')); then
#echo "python pfam_scan_to_profile.py ${infile_path}.fa $tmpdir/"
 python pfam_scan_to_profile.py ${infile_path}.fa $tmpdir $dbpath $pscan_e_val $clan_overlap
#exit;
fi

# JACKHMMER
#echo 'jackbigs';
python jackbigs.py $flag ${infile_path}.fa $tmpdir $dbpath


# Result comparison *REMOVED IN CLUSTER ADAPTATION*

#python parsejackcompare.py $tmpdir 
