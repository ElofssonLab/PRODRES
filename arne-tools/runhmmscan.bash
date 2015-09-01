#!/bin/bash 

BIN=/home/a/arnee/bin
for i in `cat $*`
do
    j=`basename $i .fa` 
    d=`dirname $i` 
    k=`echo $d| sed s/data/out/` 
    l=`echo $d| sed s/data/results/`
    if [ ! -e $k ]
    then
	mkdir -p $k
    fi
    if [ ! -e $l ]
    then
	mkdir -p $l
    fi
    if [ ! -e $k/$j.pfamout ]
    then 
	$BIN/hmmscan --cpu 6 --domtblout $l/$j.Pfam.domtbl -o  $k/$j.pfamout /pfs/nobackup/home/a/arnee/FastPSSM/data/Pfam-28/Pfam-A.hmm  $i 
    fi
    if [ ! -e $k/$j.cddout ]
    then 
	$BIN/hmmscan --cpu 6 --domtblout $l/$j.CDD.domtbl -o  $k/$j.cddout /pfs/nobackup/home/a/arnee/FastPSSM/data/CDD/CDD.hmm  $i 
    fi
done



