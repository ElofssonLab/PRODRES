#!/bin/bash 
#SBATCH -A snic2015-10-12
#SBATCH -n 1
#SBATCH -c 6
#SBATCH --time=12:00:00
#SBATCH -J RunJackhmmer
#SBATCH --output=out/jackhmmer.%J.out
#SBATCH --error=err/jackhmmer.%J.err

srun /home/a/arnee/FastPSSM/bin/runjackhmmer.bash $*
