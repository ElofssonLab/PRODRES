#!/bin/bash 

BIN=/home/a/arnee/bin
for i in $*
do
    j=`basename $i .fasta` 
    d=`dirname $i` 
    l=`echo $d| sed s/data/results/`
    if [ ! -e $l/Pfam ]
    then
	mkdir -p $l/Pfam
    fi
    if [ ! -e $l/CDD ]
    then
	mkdir -p $l/CDD
    fi
    if [ ! -e $l/Pfam/$j.pfam.domtbl ]
    then 
	$BIN/hmmscan --cpu 6 --domtblout /tmp/$j.Pfam.domtbl -o  /tmp/$j.pfamout /pfs/nobackup/home/a/arnee/FastPSSM/data/Pfam-28/Pfam-A.hmm  $i 
	mv /tmp/$j.Pfam.domtbl $l/Pfam/
    fi
    if [ ! -e $l/CDD/$j.CDD.domtbl ]
    then 
	$BIN/hmmscan --cpu 6 --domtblout /tmp/$j.CDD.domtbl -o  /tmp/$j.cddout /pfs/nobackup/home/a/arnee/FastPSSM/data/CDD/CDD.hmm  $i 
	mv /tmp/$j.Pfam.domtbl $l/CDD/
    fi
done



