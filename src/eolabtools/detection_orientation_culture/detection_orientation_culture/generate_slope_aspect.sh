#!/bin/bash
#PBS -N gen_slope_aspect
#PBS -l select=1:ncpus=4:mem=90000mb:generation=gall
#PBS -l walltime=24:00:00
#PBS -e qsub
#PBS -o qsub

module load gdal_openjpeg

cd /work/OT/eolab/DATA/BD_ORTHO/Saone-et-Loire

# gdalbuildvrt -a_srs EPSG:2154 RGE_ALTI_31_5m.vrt /work/datalake/static_aux/MNT/RGEALTI_5M_France/1_DONNEES_LIVRAISON_2020-04-00197/RGEALTI_MNT_5M_ASC_LAMB93_IGN69_D031/*.asc
gdalbuildvrt -a_srs EPSG:2154 RGE_ALTI_71_5m.vrt /datalake/static_aux/MNT/RGEALTI_5M_France/1_DONNEES_LIVRAISON_2020-04-00197/RGEALTI_MNT_5M_ASC_LAMB93_IGN69_D071/*.asc

# gdaldem slope : donne sur chaque pixel la valeur de la pente du MNT en degrés
gdaldem slope -of GTiff RGE_ALTI_71_5m.vrt  RGE_ALTI_71_5m_SLOPE.tif 

# gdaldem aspect: donne sur chaque pixel la valeur de l'orientation la pente du MNT en angle azimut (Nord = 0°, Est = 90°, Sud = 180°, Ouest = 270 °).
gdaldem aspect -of GTiff RGE_ALTI_71_5m.vrt  RGE_ALTI_71_5m_ASPECT.tif

