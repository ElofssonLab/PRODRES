#!/bin/bash
# submit jobs on uppmax
# it takes about 2-3 seconds to run one sequence with one core
nodename=`uname -n`
binpath=$DATADIR3/wk/MPTopo/src
case $nodename in 
    tintin*|*uppmax.uu.se) echo "OK, you are running from uppmax node" ;;
    triolith*) echo "OK, you are running from triolith NSC node";;
    *) echo "Error. This script should be run from uppmax login node. Exit"; exit 1;;
esac

usage="
usage: submit_run_pfam_scan_uppmax.sh fasta-seq-file [-outpath outpath] [-test]

Created 2014-11-07, updated 2014-11-07, Nanjiang Shu
"
infile=
outpath=./
#project=snic2014-8-12
project=snic2014-1-60
isTest=0
jobtime=1-24:00:00
#jobtime=00:40:00

if [ $# -lt 1 ];then
    echo "$usage"
    exit 1
fi

isNonOptionArg=false
while [ "$1" != "" ]; do
    if [ "$isNonOptionArg" == "true" ]; then 
        infile=$1
        isNonOptionArg=false
    elif [ "$1" == "--" ]; then
        isNonOptionArg=true
    elif [ "${1:0:1}" == "-" ]; then
        case $1 in
            -h | --help) PrintHelp; exit;;
            -outpath|--outpath) outpath=$2;shift;;
            -q|-quiet|--quiet) isQuiet=true;;
        -test|--test) isTest=1;;
            -*) echo "Error! Wrong argument: $1">&2; exit;;
        esac
    else
        infile=$1
    fi
    shift
done

if [ "$infile" == ""  ]; then 
    echo "infile not set. Exit" >&2
    exit 1
elif [ ! -s "$infile" ] ; then
    echo "infile '$infile' not exist or empty. Exit. " >&2
else 
    mkdir -p $outpath
    mkdir -p $outpath/log
    mkdir -p $outpath/script
    mkdir -p $outpath/splitted
    echo "Command line: $commandline"
    echo "Start at    `/bin/date`"
    res1=$(/bin/date +%s.%N)
    basename=`basename $infile`
    rootname=${basename%.*}

    numseq=`$binpath/countseq.py $infile -nf `
    if [ "$numseq" == "" ]; then 
        echo "Fatal. countseq.py error. Exit."  >&2
        exit 1
    elif [ $numseq -le 0 ] ; then
        echo "Zero sequence found in file '$infile'. Exit."  >&2
        exit 1
    else
        echo "$numseq sequences are going to be predicted by pfam_scan.pl"
        numseqperjob=` expr  20000 `
        splittedpath=$outpath/splitted
        $binpath/splitfasta.py -i $infile -nseq $numseqperjob -outpath $splittedpath -ext fa
        numsplitted=`/bin/find $splittedpath -name "*.fa" | wc -l `
        for ((i=0;i<numsplitted;i++)); do
            splittedfastafile=$splittedpath/${rootname}_${i}.fa
            logfile=$outpath/log/${rootname}_split${i}.log
            jobscriptfile=$outpath/script/run_pfam_scan_split${i}.sh
            splittedoutfile=$splittedpath/${rootname}_split${i}.pfamscan
            jobname=ps_u100_${i}
            if [ -s "$splittedfastafile" ]; then 
                echo "\
#!/bin/bash
#SBATCH -A $project
#SBATCH -n 1
#SBATCH -t $jobtime
#SBATCH -J $jobname
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kerlusshu@gmail.com
$DATADIR3/wk/MPTopo/bin/run_pfam_scan.sh $splittedfastafile -outpath $splittedpath -r \"-pfamb\" > $logfile 2>&1" > $jobscriptfile
                if [ $isTest -eq 0 ];then
                    echo "sbatch $jobscriptfile"
                    sbatch $jobscriptfile
                fi
            fi
        done
        echo "Finished at `/bin/date`"
    fi
fi
