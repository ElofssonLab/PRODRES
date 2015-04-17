#!/bin/bash -l
 


flag=$1
infile=$2
outfolder=$3
dbpath=$4
realout=$5

module rm python/2.7.2 
module load bioinfo-tools 
module load python/2.7.6 
module load biopython/1.64 
module load perl/5.18.2 
module load hmmer/3.1b1-intel 

python Trigger $realout $dbpath/ $flag $infile $outfolder 


