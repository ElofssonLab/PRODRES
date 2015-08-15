#!/bin/bash 
#SBATCH -A snic2015-10-12
# We actually start 6 jobs in parallel. Probably more efficient than running with 5 thread.
#SBATCH -n 6
#SBATCH -c 1
#SBATCH --time=24:00:00
#SBATCH -J RunJackhmmer
#SBATCH --output=out/hmmscan.%J.out
#SBATCH --error=err/hmmscan.%J.err

srun /home/a/arnee/FastPSSM/bin/runhmmscan.bash $*
