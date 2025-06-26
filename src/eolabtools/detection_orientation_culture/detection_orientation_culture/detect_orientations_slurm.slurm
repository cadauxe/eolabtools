#!/bin/bash
#
#  Launch job with command : sbatch <this file>.slurm
#  Check job with : squeue -u $USER
#

#SBATCH --job-name=orientation_culture
#SBATCH --output=slurm/outputfile-%j.out
#SBATCH --error=slurm/errorfile-%j.err
#SBATCH -N 1                        # number of nodes (or --nodes=1)
#SBATCH -n 4                        # number of tasks (or --tasks=8)
#SBATCH --mem-per-cpu=120G            # memory per core
#SBATCH --time=12:00:00             # Wall Time 10mn
#SBATCH --account=eolab      # MANDATORY : account  ( launch myaccounts to list your accounts)
#SBATCH --export=none               # To start the job with a clean environnement and source of ~/.bashrc

# module load conda/4.9.0
module load conda
conda activate /work/EOLAB/USERS/duthoit/envs/conda/detection_orientation

#cd /work/EOLAB/USERS/duthoit/ORIENTATION_DES_CULTURES/detection_orientation_culture/detection_orientation_culture
#unset PROJ_LIB

cd /work/EOLAB/USERS/guntzbp/orientation_culture/detection_orientation_culture/detection_orientation_culture

## Example on Gers 0M20
#python orientation_detection.py --img /work/EOLAB/DATA/BD_ORTHO/Gers/2019/ \
#                                 --type jp2 \
#                                 --rpg /work/EOLAB/USERS/duthoit/ORIENTATION_DES_CULTURES/RPGs/Gers/RPG_2vines_bis.shp \
#                                 --output_dir /work/EOLAB/USERS/duthoit/Nettoyage/outputs \
#                                 --nb_cores 4 \
#                                 --patch_size 10000 \
#                                 --slope /work/EOLAB/DATA/BD_ORTHO/Gers/RGE_ALTI_32_5m_SLOPE.tif \
#                                 --aspect /work/EOLAB/DATA/BD_ORTHO/Gers/RGE_ALTI_32_5m_ASPECT.tif \
#                                 --save_fld \
#                                 --verbose

## Le Havre 2017 v2
#python orientation_detection.py --img /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/PLEIADES/LeHavre/2017/LeHavre_2017_mosaic_crop.tif \
#                                 --type tif \
#                                 --rpg /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RPG/RPG_LeHavre_2017.shp \
#                                 --output_dir  /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/ORIENTATIONS/LeHavre/2017_v2 \
#                                 --nb_cores 4 \
#                                 --patch_size 10000 \
#                                 --slope /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RGE_ALTI/5m/RGE_ALTI_76_5m_SLOPE_crop.tif \
#                                 --aspect /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RGE_ALTI/5m/RGE_ALTI_76_5m_ASPECT_crop.tif \
#                                 --save_fld \
#                                 --min_nb_line_per_parcel 40 \
#                                 --min_len_line 15 \
#                                 --verbose

## Le Havre 2017 échantillon
#python orientation_detection.py --img /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/echantillon_LeHavre/echantillon_Pleiades_2017_LeHavre.tif \
#                                 --type tif \
#                                 --rpg /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/echantillon_LeHavre/echantillon_RPG_LeHavre_2017.shp \
#                                 --output_dir  /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/ORIENTATIONS/LeHavre/2017_v3 \
#                                 --nb_cores 4 \
#                                 --patch_size 10000 \
#                                 --slope /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/echantillon_LeHavre/echantillon_RGE_SLOPE.tif \
#                                 --aspect /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/echantillon_LeHavre/echantillon_RGE_ASPECT.tif \
#                                 --save_fld \
#                                 --min_nb_line_per_parcel 40 \
#                                 --min_len_line 15 \
#                                 --verbose

## Le Havre 2017 version finale après débugage : paramètres à garder pour les autres zones.
#python orientation_detection.py --img /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/PLEIADES/LeHavre/2017/LeHavre_2017_mosaic_crop.tif \
#                                 --type tif \
#                                 --rpg /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RPG/RPG_LeHavre_2017.shp \
#                                 --output_dir  /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/ORIENTATIONS/LeHavre/2017_final \
#                                 --nb_cores 4 \
#                                 --patch_size 10000 \
#                                 --slope /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RGE_ALTI/5m/RGE_ALTI_76_5m_SLOPE_crop.tif \
#                                 --aspect /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RGE_ALTI/5m/RGE_ALTI_76_5m_ASPECT_crop.tif \
#                                 --save_fld \
#                                 --min_nb_line_per_parcel 20 \
#                                 --min_len_line 8 \
#                                 --verbose


## Le Havre 2017 version finale après débugage : paramètres pas bon
#python orientation_detection.py --img /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/PLEIADES/LeHavre/2017/LeHavre_2017_mosaic_crop.tif \
#                                 --type tif \
#                                 --rpg /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RPG/RPG_LeHavre_2017.shp \
#                                 --output_dir  /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/ORIENTATIONS/LeHavre/2017_final_v2 \
#                                 --nb_cores 4 \
#                                 --patch_size 10000 \
#                                 --slope /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RGE_ALTI/5m/RGE_ALTI_76_5m_SLOPE_crop.tif \
#                                 --aspect /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RGE_ALTI/5m/RGE_ALTI_76_5m_ASPECT_crop.tif \
#                                 --save_fld \
#                                 --min_nb_line_per_parcel 15 \
#                                 --min_len_line 8 \
#                                 --verbose

# Le Havre 2023
python orientation_detection.py --img /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/PLEIADES/LeHavre/2023/LeHavre_2023_mosaic_crop.tif \
                                 --type tif \
                                 --rpg /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RPG/RPG_LeHavre_2023.shp \
                                 --output_dir  /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/ORIENTATIONS/LeHavre/2023\
                                 --nb_cores 4 \
                                 --patch_size 10000 \
                                 --slope /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RGE_ALTI/5m/RGE_ALTI_76_5m_SLOPE_crop.tif \
                                 --aspect /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RGE_ALTI/5m/RGE_ALTI_76_5m_ASPECT_crop.tif \
                                 --save_fld \
                                 --min_nb_line_per_parcel 20 \
                                 --min_len_line 8 \
                                 --verbose


# Rennes 2019
python orientation_detection.py --img /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/PLEIADES/Rennes/2019/Rennes_2019_mosaic_crop.tif \
                                 --type tif \
                                 --rpg /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RPG/RPG_Rennes_2019.shp \
                                 --output_dir  /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/ORIENTATIONS/Rennes/2019 \
                                 --nb_cores 4 \
                                 --patch_size 10000 \
                                 --slope /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RGE_ALTI/SLOPE_RGEAlti_combined_SRTM30mRAF20_flatareas.tif \
                                 --aspect /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RGE_ALTI/ASPECT_RGEAlti_combined_SRTM30mRAF20_flatareas.tif \
                                 --save_fld \
                                 --min_nb_line_per_parcel 20 \
                                 --min_len_line 8 \
                                 --verbose


# Rennes 2021
python orientation_detection.py --img /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/PLEIADES/Rennes/2021/Rennes_2021_mosaic_crop.tif \
                                 --type tif \
                                 --rpg /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RPG/RPG_Rennes_2021.shp \
                                 --output_dir  /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/ORIENTATIONS/Rennes/2021 \
                                 --nb_cores 4 \
                                 --patch_size 10000 \
                                 --slope /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RGE_ALTI/SLOPE_RGEAlti_combined_SRTM30mRAF20_flatareas.tif \
                                 --aspect /work/EOLAB/PROJET/ORIENTATION_CULTURES/SNCF_2025/RGE_ALTI/ASPECT_RGEAlti_combined_SRTM30mRAF20_flatareas.tif \
                                 --save_fld \
                                 --min_nb_line_per_parcel 20 \
                                 --min_len_line 8 \
                                 --verbose