#!/bin/bash
#SBATCH -A m2637
#SBATCH -J 2012
#SBATCH -t 00:15:00
#SBATCH -q regular
#SBATCH -C cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
#SBATCH --output=log_gridrad_mcs_2012.log
#SBATCH --mail-type=END
#SBATCH --mail-user=zhe.feng@pnnl.gov

date

module load python
source activate /global/common/software/m1867/python/pyflex

# Run Python
cd /global/homes/f/feng045/program/PyFLEXTRKR-dev/runscripts
python run_mcs_tbpfradar3d_wrf.py /global/homes/f/feng045/program/pyflex_config/config/config_gridrad_mcs_2012.yml

date