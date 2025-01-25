#!/bin/bash

#SBATCH --nodes=2
#SBATCH --ntasks=32
#SBATCH --time=04:00:00
#SBATCH --partition=amilan
#SBATCH --output=%A_%a.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=naca4005@colorado.edu
#SBATCH --array=1-141


module purge
module load anaconda
conda activate base


#reading the task id's line from the input file (eg. the job grabs the line that is respective for the array iteration)
line=$(sed -n "$[SLURM_ARRAY_TASK_ID]p" folder_names.txt)

echo "==Line: $line=="

echo "== Scripting step: running corpus.py =="
python corpus.py $line
echo "== End of Job =="