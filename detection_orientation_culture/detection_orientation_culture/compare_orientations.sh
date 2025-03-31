#!/bin/bash
#PBS -N compare_orientations
#PBS -l select=1:ncpus=24:mem=90000mb:generation=gall
#PBS -l walltime=24:00:00
#PBS -e qsub
#PBS -o qsub

module load conda/4.9.0
conda activate env_lsd

cd /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture

python compare_orientations.py --orientations_A /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude/2018/Aude_2018_0M20_lsdcmla_orientations.shp \
                               --orientations_B /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude/2018/Aude_0M20_2018_pylsd_orientations.shp \
                               --out_xls /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude/2018/comparison_Aude_2018_pylsd-lsdcmla.xls \
                               --nb_cores 24


# python compare_orientations.py --orientations_A /work/OT/eolab/taradelj/orientation_culture/output/orientations_bis.shp \
#                                --orientations_B /work/OT/eolab/taradelj/orientation_culture/output/orientations_bis.shp \
#                                --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/test_compare.csv \
#                                --nb_cores 8