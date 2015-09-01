#!/bin/bash 
# Description: make hmm database for CDD

usage="

USAGE: $0 aln-file  <outfile>

>outfile> defulat sed s/fasta\\/HMM\//
Description: make hmm database from CDD multiple alignment
aln-file is in fasta format

OPTIONS:

Created 2014-11-25, updated 2014-11-25, Nanjiang Shu

Examples:
    $0 foo/cdd/fasta//1xyz.fa  -  foo/cdd/HMM/1xyz.hmm
"

BIN=/home/a/arnee/bin/

IsProgExist(){ #{{{
    # usage: IsProgExist prog
    # prog can be both with or without absolute path
    type -P $1 &>/dev/null \
        || { echo The program \'$1\' is required but not installed. \
        Aborting $0 >&2; exit 1; }
    return 0
}
#}}}
BuildHMM(){
    local alnfile=$1
    local basename=`basename $alnfile`
    local rootname=${basename%.*}
    local dirname=`dirname $1`
    local alnfile_nocons=$tmpdir/fasta/${rootname}.nocons.fasta
    local alnfile_nocons_sto=$tmpdir/sto/${rootname}.nocons.sto
    local hmmfile=$tmpdir/hmms/${rootname}.hmm
    /home/a/arnee/git/FastPSSM/src/exclude_consensus_and_identical_from_fasta.py $alnfile -outpath $tmpdir/fasta
    seqmagick convert $alnfile_nocons $alnfile_nocons_sto
    $BIN/hmmbuild -n $rootname $hmmfile $alnfile_nocons_sto
}


if [ $# -lt 1 ]; then
    echo "$usage"
    exit
fi
infile=$1
#if [ $# -eq 2 ]; then
    outfile=`echo $1 | sed 's/fasta\//HMM\//' | sed 's/\.FASTA/\.HMM/'`
#else
#    outfile=$2
#fi


isQuiet=0
outname=
fileListFile=
fileList=()



IsProgExist seqmagick
IsProgExist "/home/a/arnee/git/FastPSSM/src/exclude_consensus_and_identical_from_fasta.py"
IsProgExist $BIN/hmmbuild
IsProgExist $BIN/hmmpress



tmpdir=$(mktemp -d /scratch/tmpdir.make_hmmdb_for_cdd.XXXXXXXXX) || { echo "Failed to create temp dir" >&2; exit 1; }
mkdir -p $tmpdir/hmms
mkdir -p $tmpdir/fasta
mkdir -p $tmpdir/sto

# echo "tmpdir = $tmpdir"




if [ -e $outfile ]
then
    # echo "outfile exist", $outfile
    exit 1 
else 
    outdir=`dirname $outfile`
    if [ ! -e $outdir ]
    then
	mkdir -p $outdir
    fi
    BuildHMM "$infile"
    mv $tmpdir/hmms/*hmm $outfile 
    $BIN/hmmpress -f $outfile
fi 


rm -rf $tmpdir
