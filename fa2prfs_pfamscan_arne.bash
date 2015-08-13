#!/bin/bash -x

set -e

if (( $# < 1 )); then
    echo "Usage: $0 <fasta file> <blast installation directory>";
    exit 1;
fi

tmpdir=$1;
infile_path=${tmpdir}query;
#filename=`basename $infile_path`
blastdir=$2;

if [[ -s ${infile_path}.prf ]]; then
    echo "$0: Found file '${infile_path}.mtx', skipping BLAST-run";
    exit ;
else
    echo "No blast result found for ${infile_path}";
fi


# This actually does the work.
python `pwd`/pfam_scan_to_profile_abisko.py ${infile_path}.fa $tmpdir/

$blastdir/bin/makeblastdb -in ${infile_path}.hits.db -dbtype prot -logfile /dev/null
$blastdir/bin/legacy_blast.pl blastpgp -j 2 -i ${infile_path}.fa -d ${infile_path}.hits.db -e 1.e-5 -v 0 -b 100 -a 4 -C ${infile_path}.chk -Q ${infile_path}.psi  -o ${infile_path}.blast   --path $blastdir/bin/   >/dev/null
python convert_psi_to_prf.py ${infile_path}.psi
