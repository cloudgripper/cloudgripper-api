#!/bin/bash
#SBATCH --gpus 1
#SBATCH -t 4:00:00
#SBATCH -A berzelius-2023-97
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user shutong@kth.se
#SBATCH -o ../../logs/slurm-%A.out
#SBATCH -e ../../logs/slurm-%A.err

module load Anaconda/2021.05-nsc1

cd /home/x_shuji/api_client_robot3/library/sbatchs

conda activate geot


python ../calculate_occlu_rate.py \
 --foam_root "/proj/berzelius-2023-54/users/x_shuji/OccluManip/Foam/" \
 --save_dir "../txt/foam_single_occu_rate_new.txt" \
 --folder_condition "Single" \
 --threshold 10000
