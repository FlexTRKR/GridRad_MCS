#!/bin/bash
#SBATCH -A m2637
#SBATCH -J 2004-2021
#SBATCH -t 00:10:00
#SBATCH -q regular
#SBATCH -C cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
#SBATCH --output=log_mcs_monthly_rainmap_gridrad_2004-2021_%A_%a.log
#SBATCH --mail-type=END
#SBATCH --mail-user=zhe.feng@pnnl.gov
#SBATCH --array=1-205

date
source activate /global/common/software/m1867/python/pyflex
# cd /global/homes/f/feng045/program/hyperfacets/mcs_v3//src/

# Takes a specified line ($SLURM_ARRAY_TASK_ID) from the task file
LINE=$(sed -n "$SLURM_ARRAY_TASK_ID"p /global/homes/f/feng045/program/hyperfacets/mcs_v3//slurm/tasklist_mcs_monthly_rainmap_gridrad_2004-2021.txt)
echo $LINE
# Run the line as a command
$LINE

date
