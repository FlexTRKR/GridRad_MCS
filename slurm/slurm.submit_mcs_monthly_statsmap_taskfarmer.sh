#!/bin/bash
#SBATCH -A m2637
#SBATCH -J statsmap
#SBATCH -t 01:30:00
#SBATCH -q regular
#SBATCH -C cpu
#SBATCH -N 4 -c 128
#SBATCH --exclusive
#SBATCH --output=log_monthly_rainmap.log
#SBATCH --mail-type=END
#SBATCH --mail-user=zhe.feng@pnnl.gov
date
module load taskfarmer
export THREADS=64
cd /global/homes/f/feng045/program/hyperfacets/mcs_v3/slurm
runcommands.sh tasklist_mcs_monthly_statsmap_gridrad_2004-2021.txt
date