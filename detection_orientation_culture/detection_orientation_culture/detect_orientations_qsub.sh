#!/bin/bash
#PBS -N orient_pylsd
#PBS -l select=1:ncpus=24:mem=180000mb:generation=gall
#PBS -l walltime=24:00:00
#PBS -e qsub
#PBS -o qsub

module load conda/4.9.0
conda activate detection_orientation

cd /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture
unset PROJ_LIB

# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/BDORTHO_Aude_2018/ORTHOHR_1-0_RVB-0M20_JP2-E080_LAMB93_D011_2018-01-01/ORTHOHR/1_DONNEES_LIVRAISON_2020-07-00005/OHR_RVB_0M20_JP2-E080_LAMB93_D11-2018/11-2018-0615-6190-LA93-0M20-E080.jp2 \
#                                --type jp2 \
#                                --rpg /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/extrait_rpg_aude_2018.shp \
#                                --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/aude_test.shp \
#                                --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/aude_test.csv \
#                                --nb_cores 8 \
#                                --patch_size 10000 \
#                                --slope /work/OT/eolab/guntzbp/Flaude/DEM/RGE_ALTI_5m_SLOPE_D011.tif \
#                                --aspect /work/OT/eolab/guntzbp/Flaude/DEM/RGE_ALTI_5m_ASPECT_D011.tif \
#                                --save_lsd \
#                                --verbose
# AUDE 0M50
# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/BDORTHO_2-0_RVB-0M50_JP2-E080_LAMB93_D011_2015-01-01/BDORTHO/1_DONNEES_LIVRAISON_2016-05-00226/BDO_RVB_0M50_JP2-E080_LAMB93_D11-2015 \
#                                  --type jp2 \
#                                  --rpg /work/EXT/SCO/FLAUDE/RPG/Aude/2015/IGN_RPG_20150101/IGN_RPG_20150101_AUDE.shp \
#                                  --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude_2015.shp \
#                                  --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude_2015.csv \
#                                  --nb_cores 24 \
#                                  --patch_size 10000 \
#                                  --slope /work/OT/eolab/guntzbp/Flaude/DEM/RGE_ALTI_5m_SLOPE_D011.tif \
#                                  --aspect /work/OT/eolab/guntzbp/Flaude/DEM/RGE_ALTI_5m_ASPECT_D011.tif \
#                                  --save_lsd

# AUDE 0M20
# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/BDORTHO_Aude_2018/ORTHOHR_1-0_RVB-0M20_JP2-E080_LAMB93_D011_2018-01-01/ORTHOHR/1_DONNEES_LIVRAISON_2020-07-00005/OHR_RVB_0M20_JP2-E080_LAMB93_D11-2018 \
#                                --type jp2 \
#                                --rpg /work/EXT/SCO/FLAUDE/RPG/Aude/2018/PARCELLES_GRAPHIQUES_Aude_2018.shp \
#                                --railroad_file /work/OT/eolab/DATA/SNCF/dataSNCF/formes-des-lignes-du-rfn.shp \
#                                --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude/2018/Aude_0M20_2018_pylsd.shp \
#                                --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude/2018/Aude_0M20_2018_pylsd.csv \
#                                --nb_cores 24 \
#                                --patch_size 10000 \
#                                --slope /work/OT/eolab/guntzbp/Flaude/DEM/RGE_ALTI_5m_SLOPE_D011.tif \
#                                --aspect /work/OT/eolab/guntzbp/Flaude/DEM/RGE_ALTI_5m_ASPECT_D011.tif \
#                                --save_lsd \
#                                --verbose

# Gironde 0M20
# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/Gironde \
#                                 --type jp2 \
#                                 --rpg /work/OT/eolab/DATA/RPG/2015/1_DONNEES_LIVRAISON_2015/RPG_2-0_SHP_LAMB93_R75-2015/RPG_Gironde_2015.shp \
#                                 --railroad_file /work/OT/eolab/DATA/SNCF/dataSNCF/formes-des-lignes-du-rfn.shp \
#                                 --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Gironde_0M20_2018_pylsd.shp \
#                                 --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Gironde_0M20_2018_pylsd.csv \
#                                 --nb_cores 24 \
#                                 --patch_size 10000 \
#                                 --slope /work/OT/eolab/DATA/BD_ORTHO/Gironde/RGE_ALTI_33_5m_SLOPE.tif \
#                                 --aspect /work/OT/eolab/DATA/BD_ORTHO/Gironde/RGE_ALTI_33_5m_ASPECT.tif \
#                                 --save_lsd

# Gers 0M20
python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/Gers \
                                --type jp2 \
                                --rpg /work/OT/eolab/DATA/RPG/2019_departements/RPG_Gers_32_2019.shp \
                                --railroad_file /work/OT/eolab/DATA/SNCF/dataSNCF/formes-des-lignes-du-rfn.shp \
                                --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Gers/Gers_0M20_2019_pylsd.shp \
                                --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Gers/Gers_0M20_2019_pylsd.csv \
                                --nb_cores 24 \
                                --patch_size 10000 \
                                --slope /work/OT/eolab/DATA/BD_ORTHO/Gers/RGE_ALTI_32_5m_SLOPE.tif \
                                --aspect /work/OT/eolab/DATA/BD_ORTHO/Gers/RGE_ALTI_32_5m_ASPECT.tif \
                                --save_lsd \
                                --verbose

# Ariege 0M20
# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/Ariège/ORTHOHR_1-0_RVB-0M20_JP2-E080_LAMB93_D009_2019-01-01/ORTHOHR/1_DONNEES_LIVRAISON_2020-08-00186/OHR_RVB_0M20_JP2-E080_LAMB93_D09-2019 \
#                                 --type jp2 \
#                                 --rpg /work/OT/eolab/DATA/RPG/2019_departements/RPG_Ariege_09_2019.shp \
#                                 --railroad_file /work/OT/eolab/DATA/SNCF/dataSNCF/formes-des-lignes-du-rfn.shp \
#                                 --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Ariege/Ariege_2019_0M20_pylsd.shp \
#                                 --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Ariege/Ariege_2019_0M20_pylsd.csv \
#                                 --nb_cores 24 \
#                                 --patch_size 10000 \
#                                 --slope /work/OT/eolab/DATA/BD_ORTHO/Ariège/RGE_ALTI_09_5m_SLOPE.tif \
#                                 --aspect /work/OT/eolab/DATA/BD_ORTHO/Ariège/RGE_ALTI_09_5m_ASPECT.tif \
#                                 --save_lsd
#                                 --verbose

# Tarn-et-Garonne
# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/D082_TarnEtGaronne/ORTHOHR_1-0_RVB-0M20_JP2-E080_LAMB93_D082_2019-01-01/ORTHOHR/1_DONNEES_LIVRAISON_2019-11-00141/OHR_RVB_0M20_JP2-E080_LAMB93_D82-2019 \
#                                --type jp2 \
#                                --rpg /work/OT/eolab/DATA/RPG/2019_departements/RPG_Tarn-et-Garonne_82_2019.shp \
#                                --railroad_file /work/OT/eolab/DATA/SNCF/dataSNCF/formes-des-lignes-du-rfn.shp \
#                                --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Tarn-et-Garonne/Tarn-et-Garonne_0M20_2019_pylsd.shp \
#                                --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Tarn-et-Garonne/Tarn-et-Garonne_0M20_2019_pylsd.csv \
#                                --nb_cores 24 \
#                                --patch_size 10000 \
#                                --slope /work/OT/eolab/DATA/BD_ORTHO/D082_TarnEtGaronne/RGE_ALTI_82_5m_SLOPE.tif \
#                                --aspect /work/OT/eolab/DATA/BD_ORTHO/D082_TarnEtGaronne/RGE_ALTI_82_5m_ASPECT.tif \
#                                --save_lsd \
#                                --verbose

# Cote-d'Or
# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/Cote-d-Or \
#                                --type jp2 \
#                                --rpg /work/OT/eolab/DATA/RPG/2020_departements/RPG_Cote-d-Or_21_2020.shp \
#                                --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Cote-d-Or/Cote-d-Or_0M20_2020_pylsd.shp \
#                                --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Cote-d-Or/Cote-d-Or_0M20_2020_pylsd.csv \
#                                --railroad_file /work/OT/eolab/DATA/SNCF/dataSNCF/formes-des-lignes-du-rfn.shp \
#                                --nb_cores 24 \
#                                --patch_size 10000 \
#                                --slope /work/OT/eolab/DATA/BD_ORTHO/Cote-d-Or/RGE_ALTI_21_5m_SLOPE.tif \
#                                --aspect /work/OT/eolab/DATA/BD_ORTHO/Cote-d-Or/RGE_ALTI_21_5m_ASPECT.tif \
#                                --save_lsd \
#                                --verbose

# Ille-et-Vilaine
# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/Ille-et-Vilaine \
#                                --type jp2 \
#                                --rpg /work/OT/eolab/DATA/RPG/2020_departements/RPG_Ille-et-Vilaine_35_2020.shp \
#                                --railroad_file /work/OT/eolab/DATA/SNCF/dataSNCF/formes-des-lignes-du-rfn.shp \
#                                --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Ille-et-Vilaine/Ille-et-Vilaine_0M20_2020_pylsd.shp \
#                                --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Ille-et-Vilaine/Ille-et-Vilaine_0M20_2020_pylsd.csv \
#                                --nb_cores 24 \
#                                --patch_size 10000 \
#                                --slope /work/OT/eolab/DATA/BD_ORTHO/Ille-et-Vilaine/RGE_ALTI_35_5m_SLOPE.tif \
#                                --aspect /work/OT/eolab/DATA/BD_ORTHO/Ille-et-Vilaine/RGE_ALTI_35_5m_ASPECT.tif \
#                                --save_lsd \
#                                --verbose

# Haut-Rhin
# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/Haut-Rhin \
#                                --type jp2 \
#                                --rpg /work/OT/eolab/DATA/RPG/2018/1_DONNEES_LIVRAISON_2018/RPG_2-0_SHP_LAMB93_R44-2018/RPG_Haut-Rhin_2018.shp \
#                                --railroad_file /work/OT/eolab/DATA/SNCF/dataSNCF/formes-des-lignes-du-rfn.shp \
#                                --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Haut-Rhin/Haut-Rhin_0M20_2020_pylsd.shp \
#                                --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Haut-Rhin/Haut-Rhin_0M20_2020_pylsd.csv \
#                                --nb_cores 24 \
#                                --patch_size 10000 \
#                                --slope /work/OT/eolab/DATA/BD_ORTHO/Haut-Rhin/RGE_ALTI_68_5m_SLOPE.tif \
#                                --aspect /work/OT/eolab/DATA/BD_ORTHO/Haut-Rhin/RGE_ALTI_68_5m_ASPECT.tif \
#                                --save_lsd \
#                                --verbose

# Haute-Saone
# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/Haute-Saone \
#                                --type jp2 \
#                                --rpg /work/OT/eolab/DATA/RPG/2020_departements/RPG_Haute-Saone_70_2020.shp \
#                                --railroad_file /work/OT/eolab/DATA/SNCF/dataSNCF/formes-des-lignes-du-rfn.shp \
#                                --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Haute-Saone/Haute-Saone_0M20_2020_pylsd.shp \
#                                --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Haute-Saone/Haute-Saone_0M20_2020_pylsd.csv \
#                                --nb_cores 24 \
#                                --patch_size 10000 \
#                                --slope /work/OT/eolab/DATA/BD_ORTHO/Haute-Saone/RGE_ALTI_70_5m_SLOPE.tif \
#                                --aspect /work/OT/eolab/DATA/BD_ORTHO/Haute-Saone/RGE_ALTI_70_5m_ASPECT.tif \
#                                --save_lsd
#                                --verbose

# Jura
# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/Jura \
#                                --type jp2 \
#                                --rpg /work/OT/eolab/DATA/RPG/2020_departements/RPG_Jura_39_2020.shp \
#                                --railroad_file /work/OT/eolab/DATA/SNCF/dataSNCF/formes-des-lignes-du-rfn.shp \
#                                --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Jura/Jura_0M20_2020_pylsd.shp \
#                                --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Jura/Jura_0M20_2020_pylsd.csv \
#                                --nb_cores 24 \
#                                --patch_size 10000 \
#                                --slope /work/OT/eolab/DATA/BD_ORTHO/Jura/RGE_ALTI_39_5m_SLOPE.tif \
#                                --aspect /work/OT/eolab/DATA/BD_ORTHO/Jura/RGE_ALTI_39_5m_ASPECT.tif \
#                                --save_lsd
#                                --verbose

# Haute Garonne 0M20
# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/Haute_Garonne \
#                                 --type jp2 \
#                                 --rpg /work/OT/eolab/DATA/RPG/2019_departements/RPG_Haute-Garonne_31_2019.shp \
#                                 --railroad_file /work/OT/eolab/DATA/SNCF/dataSNCF/formes-des-lignes-du-rfn.shp \
#                                 --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Haute_Garonne/Haute_Garonne_0M20_2019_lsd.shp \
#                                 --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Haute_Garonne/Haute_Garonne_0M20_2019_lsd.csv \
#                                 --nb_cores 24 \
#                                 --patch_size 10000 \
#                                 --slope /work/OT/eolab/DATA/BD_ORTHO/Haute_Garonne/RGE_ALTI_31_5m_SLOPE.tif \
#                                 --aspect /work/OT/eolab/DATA/BD_ORTHO/Haute_Garonne/RGE_ALTI_31_5m_ASPECT.tif \
#                                 --save_lsd

# Hérault 0M20
# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/Hérault/ORTHOHR_1-0_RVB-0M20_JP2-E080_LAMB93_D034_2018-01-01/ORTHOHR/1_DONNEES_LIVRAISON_2019-09-00246/OHR_RVB_0M20_JP2-E080_LAMB93_D34-2018 \
#                                 --type jp2 \
#                                 --rpg /work/OT/eolab/DATA/RPG/2018/1_DONNEES_LIVRAISON_2018/RPG_2-0_SHP_LAMB93_R76-2018/RPG_Herault_2018.shp \
#                                 --railroad_file /work/OT/eolab/DATA/SNCF/dataSNCF/formes-des-lignes-du-rfn.shp \
#                                 --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Herault_pyLSD_2018.shp \
#                                 --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Herault_pyLSD_2018.csv \
#                                 --nb_cores 24 \
#                                 --patch_size 10000 \
#                                 --slope /work/OT/eolab/DATA/BD_ORTHO/Hérault/RGE_ALTI_34_5m_SLOPE.tif \
#                                 --aspect /work/OT/eolab/DATA/BD_ORTHO/Hérault/RGE_ALTI_34_5m_ASPECT.tif \
#                                 --save_lsd

# Saone-et-Loire 0M20
# python orientation_detection.py --img /work/OT/eolab/DATA/BD_ORTHO/Saone-et-Loire/ORTHOHR_1-0_RVB-0M20_JP2-E080_LAMB93_D071_2020-01-01/ORTHOHR/1_DONNEES_LIVRAISON_2021-06-00132/OHR_RVB_0M20_JP2-E080_LAMB93_D71-2020 \
#                                 --type jp2 \
#                                 --rpg /work/OT/eolab/DATA/RPG/2020_departements/RPG_Saone-et-Loire_71_2020.shp \
#                                 --railroad_file /work/OT/eolab/DATA/SNCF/dataSNCF/formes-des-lignes-du-rfn.shp \
#                                 --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Saone-et-Loire/Saone-et-Loire_0M20_2020_pylsd.shp \
#                                 --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Saone-et-Loire/Saone-et-Loire_0M20_2020_pylsd.csv \
#                                 --nb_cores 24 \
#                                 --patch_size 10000 \
#                                 --slope /work/OT/eolab/DATA/BD_ORTHO/Saone-et-Loire/RGE_ALTI_71_5m_SLOPE.tif \
#                                 --aspect /work/OT/eolab/DATA/BD_ORTHO/Saone-et-Loire/RGE_ALTI_71_5m_ASPECT.tif \
#                                 --save_lsd
