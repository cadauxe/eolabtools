#!/bin/bash
#PBS -N orient_pylsd_aude
#PBS -l select=1:ncpus=4:mem=80000mb:generation=gall
#PBS -l walltime=1:00:00

module load conda/4.9.0
conda activate /work/EOLAB/USERS/duthoit/envs/conda/detection_orientation

cd /work/EOLAB/USERS/duthoit/ORIENTATION_DES_CULTURES/detection_orientation_culture/detection_orientation_culture
unset PROJ_LIB

# Example on Gers 0M20

 python orientation_detection.py --img /work/EOLAB/DATA/BD_ORTHO/Gers/2019/ \
                                 --type jp2 \
                                 --rpg /work/EOLAB/USERS/duthoit/ORIENTATION_DES_CULTURES/RPGs/Gers/RPG_2vines_bis.shp \
                                 --output_dir /work/EOLAB/USERS/duthoit/Nettoyage/outputs \
                                 --nb_cores 4 \
                                 --patch_size 10000 \
                                 --slope /work/EOLAB/DATA/BD_ORTHO/Gers/RGE_ALTI_32_5m_SLOPE.tif \
                                 --aspect /work/EOLAB/DATA/BD_ORTHO/Gers/RGE_ALTI_32_5m_ASPECT.tif \
                                 --save_fld \
                                 --verbose



