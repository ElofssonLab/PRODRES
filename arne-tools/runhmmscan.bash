#!/bin/bash -x

for k in $*
do
    find $k -type f -name "*.fa" -exec  sh -c ' j=`basename {} .fa` ; i=`dirname {}` k=`echo $i| sed s/data/out/` ; l=`echo $i| sed s/data/results/`; if [ ! -e $k/$j.pfamout ] ; then hmmscan --cpu 1 --domtblout $l/$j.domtblout -o  $k/$j.pfamout /pfs/nobackup/home/a/arnee/FastPSSM/data/Pfam-28/Pfam-A.hmm  {} ; else  echo $j ; fi ' \; 
done



