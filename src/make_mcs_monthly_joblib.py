"""
Make task list and slurm script (Job Array) to calculate monthly MCS statistics.

Example task list:
python calc_tbpf_mcs_monthly_rainmap_gridrad.py config.yml 2018 6
python calc_tbpf_mcs_monthly_rainmap_gridrad.py config.yml 2018 7
python calc_tbpf_mcs_monthly_rainmap_gridrad.py config.yml 2018 8
...

Each line will be submitted as a slurm job using Job Array.
"""
import sys
import textwrap
import subprocess
import pandas as pd

if __name__ == "__main__":

    # Get inputs from command line
    start_date = sys.argv[1]
    end_date = sys.argv[2]
    # Examples:
    # start_date = '2018-6'
    # end_date = '2019-5'

    # Submit job at run time
    submit_job = False

    period = f"{start_date[0:4]}-{end_date[0:4]}"
    task_type = f"mcs_monthly_rainmap_gridrad"
    # task_type = f"mcs_monthly_statsmap_gridrad"

    # Slurm wall clock time
    wallclock_time = '00:10:00'

    # Python analysis code name
    root_dir = "/global/homes/f/feng045/program/hyperfacets/mcs_v3/"
    code_dir = f"{root_dir}/src/"
    python_codename = f"python {code_dir}calc_tbpf_mcs_monthly_rainmap_gridrad.py"
    # python_codename = f"{code_dir}run_mcs_monthly_statsmap.sh"

    # Tracking config file
    config_dir = f"{root_dir}/config/"
    config_basename="config_gridrad_mcs_"

    # Make task and slurm file name
    task_filename = f"{root_dir}/slurm/tasklist_{task_type}_{period}.txt"
    slurm_filename = f"{root_dir}/slurm/slurm.submit_{task_type}_{period}.sh"


    # Make monthly start dates for the tracking period
    start_dates = pd.date_range(f'{start_date}', f'{end_date}', freq='1MS')

    # Create the list of job tasks needed by SLURM...
    task_file = open(task_filename, "w")
    ntasks = 0

    # Create task commands
    for idate in start_dates:
        config_file = f"{config_dir}{config_basename}{idate.year}.yml"
        cmd = f"{python_codename} {config_file} {idate.year} {idate.month}"
        task_file.write(f"{cmd}\n")
        ntasks += 1
    task_file.close()
    print(task_filename)

    # Create a SLURM submission script for the above task list...
    slurm_file = open(slurm_filename, "w")
    text = f"""\
        #!/bin/bash
        #SBATCH -A m2637
        #SBATCH -J {period}
        #SBATCH -t {wallclock_time}
        #SBATCH -q regular
        #SBATCH -C cpu
        #SBATCH --nodes=1
        #SBATCH --ntasks-per-node=128
        #SBATCH --exclusive
        #SBATCH --output=log_{task_type}_{period}_%A_%a.log
        #SBATCH --mail-type=END
        #SBATCH --mail-user=zhe.feng@pnnl.gov
        #SBATCH --array=1-{ntasks}

        date
        source activate /global/common/software/m1867/python/pyflex
        # cd {code_dir}

        # Takes a specified line ($SLURM_ARRAY_TASK_ID) from the task file
        LINE=$(sed -n "$SLURM_ARRAY_TASK_ID"p {task_filename})
        echo $LINE
        # Run the line as a command
        $LINE

        date
        """
    slurm_file.writelines(textwrap.dedent(text))
    slurm_file.close()
    print(slurm_filename)

    # Run command
    if submit_job == True:
        # cmd = f'sbatch --array=1-{ntasks}%{njobs_run} {slurm_filename}'
        cmd = f'sbatch --array=1-{ntasks} {slurm_filename}'
        print(cmd)
        subprocess.run(f'{cmd}', shell=True)