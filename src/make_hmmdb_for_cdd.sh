#!/bin/bash
# Description: make hmm database for CDD

usage="
USAGE: $0 aln-file [aln-file...] [-l aln-file-list] -outname STR

Description: make hmm database from CDD multiple alignment
aln-file is in fasta format

OPTIONS:
    -hmmbin STR  Set the binpath for hmm executables, (default: /usr/bin)

Created 2014-11-25, updated 2014-11-25, Nanjiang Shu

Examples:
    $0 -l cdd.msa.filelist -outname cddhmm/cdd.hmm
"

hmmbin=/usr/bin

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
    local alnfile_nocons=$tmpdir/fasta/${rootname}.nocons.fasta
    local alnfile_nocons_sto=$tmpdir/sto/${rootname}.nocons.sto
    local hmmfile=$tmpdir/hmms/${rootname}.hmm
    $DATADIR3/wk/MPTopo/src/exclude_consensus_from_fasta.py $alnfile -outpath $tmpdir/fasta
    seqmagick convert $alnfile_nocons $alnfile_nocons_sto
    $hmmbin/hmmbuild -n $rootname $hmmfile $alnfile_nocons_sto
}

if [ $# -lt 1 ]; then
    echo "$usage"
    exit
fi

isQuiet=0
outname=
fileListFile=
fileList=()


isNonOptionArg=0
while [ "$1" != "" ]; do
    if [ $isNonOptionArg -eq 1 ]; then 
        fileList+=("$1")
        isNonOptionArg=0
    elif [ "$1" == "--" ]; then
        isNonOptionArg=true
    elif [ "${1:0:1}" == "-" ]; then
        case $1 in
            -h | --help) echo "$usage"; exit;;
            -outname|--outname) outname=$2;shift;;
            -hmmbin|--hmmbin) hmmbin=$2;shift;;
            -l|--l|-list|--list) fileListFile=$2;shift;;
            -q|-quiet|--quiet) isQuiet=1;;
            -*) echo Error! Wrong argument: $1 >&2; exit;;
        esac
    else
        fileList+=("$1")
    fi
    shift
done

if [ "$outname" == "" ];then
    echo "$0: outname not set. exit"
    exit 1
fi

IsProgExist seqmagick
IsProgExist "$DATADIR3/wk/MPTopo/src/exclude_consensus_from_fasta.py"
IsProgExist "$hmmbin/hmmbuild"
IsProgExist "$hmmbin/hmmpress"

if [ "$fileListFile" != ""  ]; then 
    if [ -s "$fileListFile" ]; then 
        while read line
        do
            fileList+=("$line")
        done < $fileListFile
    else
        echo listfile \'$fileListFile\' does not exist or empty. >&2
    fi
fi

numFile=${#fileList[@]}
if [ $numFile -eq 0  ]; then
    echo $0: Input not set! Exit. >&2
    exit 1
fi

tmpdir=$(mktemp -d /scratch/tmpdir.make_hmmdb_for_cdd.XXXXXXXXX) || { echo "Failed to create temp dir" >&2; exit 1; }
mkdir -p $tmpdir/hmms
mkdir -p $tmpdir/fasta
mkdir -p $tmpdir/sto

echo "tmpdir = $tmpdir"

for ((i=0;i<numFile;i++));do
    file=${fileList[$i]}
    BuildHMM "$file"
done

dir_outname=`dirname $outname`
if [ ! -d "$dir_outname" ];then
    mkdir -p $dir_outname
fi


find $tmpdir/hmms -name "*.hmm" -print0 | xargs -0 cat > $outname
$hmmbin/hmmpress -f $outname

rm -rf $tmpdir
