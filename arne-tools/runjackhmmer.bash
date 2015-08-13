#!/bin/bash -x

for i in $*
do
    OUT=`echo $i | sed s/data/out/g | sed s/\.fa$/\.out/g`
    ERR=`echo $i | sed s/data/out/g | sed s/\.fa$/\.err/g`
    RESOUT=`echo $i | sed s/data/results/g | sed s/\.fa$/\.out/g`
    RESDOM=`echo $i | sed s/data/results/g | sed s/\.fa$/\.domtab/g`
    if [ ! -e $RESDOM ]
    then
	touch $RESDOM
	time /home/a/arnee/bin/jackhmmer --cpu 6 --noali --notextw --domtblout $RESDOM -o $RESOUT $i /pfs/nobackup/home/a/arnee/FastPSSM/data/pfamfull/uniref100.pfam27.pfamseq.nr90.fasta  
    fi
done



