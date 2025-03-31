#!/bin/bash
#SBATCH --job-name=sunmap       # job's name
#SBATCH --output=outfile-%j.out
#SBATCH --error=errfile-%j.err
#SBATCH -N 1                        # number of nodes (or --nodes=1)
#SBATCH -n 32                        # number of tasks (or --tasks=8)
#SBATCH --mem-per-cpu=20000M         # memory per core
#SBATCH --time=12:00:00             # Wall Time
#SBATCH --account=eolab       # MANDATORY : account  ( launch myaccounts to list your accounts)
#SBATCH --export=none               # To start the job with a clean environnement and source of ~/.bashrc

ml conda
conda activate /work/EOLAB/USERS/duthoit/envs/conda/crt_enso/

cd /work/EOLAB/USERS/duthoit/CARTE_ENSOILLEMENT/sun_map_generation/src/

python SunMapGenerator.py --digital_surface_model /work/EOLAB/USERS/duthoit/CARTE_ENSOILLEMENT/sun_map_generation/listings/listing.lst \
                          --tiles_file /work/EOLAB/DATA/MNS/Paris/dalles.shp \
                          --area Paris \
                          --date 2024-07-21  \
                          --time 11:00 17:00 60 \
                          --nb_cores 32 \
                          --occ_changes 4 \
                          --output_dir /work/EOLAB/USERS/duthoit/CARTE_ENSOILLEMENT/outputs/test/ \
                          --save_temp \
                          --save_masks