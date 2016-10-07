#!/bin/bash -l
 
#SBATCH -A snic2014-8-12
#SBATCH -p core
#SBATCH -n 2
#SBATCH -t 180:00
#SBATCH -J fastDBscan

flag=$1
infile=$2
outfolder=$3

module rm python/2.7.2
module load bioinfo-tools
module load python/2.7.6
module load biopython/1.64
module load perl/5.18.2
module load hmmer/3.1b1-intel

python SAVE_Trigger $SLURM_JOB_ID $flag $infile $outfolder 
