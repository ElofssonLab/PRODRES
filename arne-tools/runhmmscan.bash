#!/bin/bash -x

BIN=/home/a/arnee/FastPSSM/bin
for i in $*
do
    j=`basename $i .fa` 
    d=`dirname $i` 
    k=`echo $i| sed s/data/out/` 
    l=`echo $i| sed s/data/results/`
    if [ ! -e $k/$j.pfamout ]
    then 
	$BIN/hmmscan --cpu 6 --domtblout $l/$j.Pfam -o  $k/$j.pfamout /pfs/nobackup/home/a/arnee/FastPSSM/data/Pfam-28/Pfam-A.hmm  $i 
    fi
    if [ ! -e $k/z$j.cddout ]
    then 
	$BIN/hmmscan --cpu 6 --domtblout $l/$j.CDD -o  $k/$j.cddout /pfs/nobackup/home/a/arnee/FastPSSM/data/CDD/CDD.hmm  $i 
    fi
done



