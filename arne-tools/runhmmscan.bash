#!/bin/bash -x

for k in $*
do
    find $k -type f -name "*.fa" -exec  sh -c ' j=`basename {} .fa` ; i=`dirname {}` ; if [ ! -e $i/$j.pfamout ] ; then hmmscan --cpu 1 --domtblout $i/$j.domtblout -o  $i/$j.pfamout /pfs/nobackup/home/a/arnee/FastPSSM/data/Pfam-28/Pfam-A.hmm  {} ; else  echo $j ; fi ' \; 
done



