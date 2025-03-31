#!/bin/bash
#PBS -N LSD_CMLA
#PBS -l select=1:ncpus=12:mem=90000mb:generation=gall
#PBS -l walltime=24:00:00
#PBS -e qsub
#PBS -o qsub


cd /work/OT/eolab/guntzbp/build/LSD
module load otb/7.0
#!/usr/bin/sh
APPLICATION_DIR=`pwd`
echo "**** Update environment variables for application built under ${APPLICATION_DIR} ****"
export OTB_APPLICATION_PATH=${APPLICATION_DIR}/lib/otb/applications/:$OTB_APPLICATION_PATH
export LD_LIBRARY_PATH=${APPLICATION_DIR}/lib:${LD_LIBRARY_PATH}
export PATH=${APPLICATION_DIR}/bin:$PATH

cd /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture

# Aude 0M50 list
# python lsd_cmla.py --img /work/OT/eolab/DATA/BD_ORTHO/BDORTHO_2-0_RVB-0M50_JP2-E080_LAMB93_D011_2015-01-01/BDORTHO/1_DONNEES_LIVRAISON_2016-05-00226/BDO_RVB_0M50_JP2-E080_LAMB93_D11-2015 \
#                     --type jp2 \
#                     --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude_0M50_lsdcmla.shp \
#                     --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude_0M50_lsdcmla.csv \
#                     --nb_cores 24 \

# Aude 0M50 mosaique
python lsd_cmla.py --img /work/OT/eolab/DATA/BD_ORTHO/BDO_RVB_0M50_LAMB93_D11_2015.tif \
                    --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude_0M50_lsdcmla.shp \
                    --out_csv /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude_0M50_lsdcmla.csv \
                    --nb_cores 24 \