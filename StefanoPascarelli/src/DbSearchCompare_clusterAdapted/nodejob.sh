#!/bin/bash -l

#SBATCH -A snic2014-8-12 
#SBATCH -p node
#SBATCH -N 1
#SBATCH -n 16
#SBATCH -t 46:00:00
# 

echo "NODEJOB.SH"

module rm python/2.7.2
module load bioinfo-tools
module load python/2.7.6
module load biopython/1.64
module load perl/5.18.2
module load hmmer/3.1b1-intel



if [ "$SNIC_TMP" != "" ]; then

    TMPDIR=$SNIC_TMP

else

    if [ -d /scratch ];then

        TMPDIR=/scratch/$$

    elif [ -d /tmp ];then

        TMPDIR=/tmp/$$

    else

        TMPDIR=tmp/$$

    fi

fi





if [ ! -d $TMPDIR ] ; then 

    mkdir -p $TMPDIR

fi
TMPDIR="$TMPDIR/"
#echo "cp -rf ../pfam/ $TMPDIR"
#cp -rf ../pfam/ $TMPDIR

echo "python provaslowoverwatch.py $TMPDIR"
python provaslowoverwatch.py $TMPDIR
