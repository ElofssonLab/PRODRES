#!/bin/bash 
#SBATCH -A snic2015-10-12
# We actually start 6 jobs in parallel. 
# Probably more efficient than running with 5 thread.
#SBATCH -n 6
#SBATCH -c 1
#SBATCH --time=24:00:00
#SBATCH -J RunJackhmmer
#SBATCH --output=out/hmmscan.%J.out
#SBATCH --error=err/hmmscan.%J.err

for i in data/uniref100.fasta.split-*.names
do 
    j=`basename $i`
    if [ !  -e out/$j.out ]
    then
	srun -A snic2015-10-12 --time=24:00:00 -n 1 -c 6 /home/a/arnee/FastPSSM/bin/runhmmscan.bash $i 
#	/home/a/arnee/FastPSSM/bin/runhmmscan.bash $i
    fi
done
