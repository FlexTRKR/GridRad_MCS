#!/bin/bash
#SBATCH -A m2637
#SBATCH -J monthmap
#SBATCH -t 00:30:00
#SBATCH -q debug
#SBATCH -C cpu
#SBATCH -N 2 -c 128
#SBATCH --exclusive
#SBATCH --output=log_monthly_rainmap.log
#SBATCH --mail-type=END
#SBATCH --mail-user=zhe.feng@pnnl.gov
date
module load taskfarmer
export THREADS=128
cd /global/homes/f/feng045/program/hyperfacets/mcs_v3
runcommands.sh tasklist_mcs_monthly_rainmap_gridrad.txt
date