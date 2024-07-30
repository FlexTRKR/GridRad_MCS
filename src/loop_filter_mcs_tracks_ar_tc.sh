#!/bin/bash

# This script runs the Python code filter_mcs_tracks_ar_tc.py for a list of years

# module load python
source activate /global/common/software/m1867/python/py310

STARTYEAR=2004
ENDYEAR=2017
# STARTYEAR=2018
# ENDYEAR=2021
config_file='config_gpm_conus.yml'

# Loop over each year
for iyear in $(seq ${STARTYEAR} ${ENDYEAR}); do
    year1=$((${iyear}+1))
    # Full year
    idates=${iyear}0101.0000_${year1}0101.0000
    # Partial year
    # idates=${iyear}0401.0000_${iyear}0901.0000
    echo ${idates}
    python filter_mcs_tracks_ar_tc.py ${idates} ${config_file}
done
