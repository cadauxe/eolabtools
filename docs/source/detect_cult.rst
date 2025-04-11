.. _detect_cult:

=============================
Detection Orientation Culture
=============================


## Calcul des données utilisées dans le calcul des orientations

Il faut en premier lieu récupérer les informations issues du MNT pour récupérer la pente moyenne et l'orientation moyenne de la pente sur chaque parcelle.
Cette étape se fait à l'aide du script `generate_slope_aspect.sh` et se divise en plusieurs sous-tâches :

Pour créer le MNT monolithique pour un département donnée (ici le 11 : l'Aude), utiliser la commande `gdalbuildvrt` :

```
gdalbuildvrt -a_srs EPSG:2154 RGE_ALTI_11_5m.vrt /work/datalake/static_aux/MNT/RGEALTI_5M_France/1_DONNEES_LIVRAISON_2020-04-00197/RGEALTI_MNT_5M_ASC_LAMB93_IGN69_D011/*.asc
```

On peut ensuite calculer l'angle de la pente ainsi que l'orientation de la pente dans deux rasters avec `gdaldem` :

```
# gdaldem slope : donne sur chaque pixel la valeur de la pente du MNT en degrés
gdaldem slope of GTiff RGE_ALTI_11_5m.vrt  RGE_ALTI_11_5m_SLOPE.tif

# gdaldem aspect: donne sur chaque pixel la valeur de l'orientation la pente du MNT en angle azimut (Nord = 0°, Est = 90°, Sud = 180°, Ouest = 270 °).
gdaldem aspect of GTiff RGE_ALTI_11_5m.vrt  RGE_ALTI_11_5m_ASPECT.tif
```
Ces rasters seront utilisés dans le traitement final calculant l'orientation des parcelles.



## Fichiers de code contenus dans le répertoire

- `detection_orientation_culture/orientation_detection.py`: code pour détecter l'orientation des cultures à l'aide de l'algorithme de détection de segment fld.
- `detection_orientation_culture/detect_orientation_qsub.sh` : script qsub permettant de lancer un job sur le cluster pour le calcul de la détection des orientations à l'aide de fld.



# En utilisant les scripts qsub :

## Détection de l'orientation des cultures avec fld

Pour obtenir l'orientation des cultures dans un fichier shapefile, il faut utiliser le script `detect_orientation_qsub.sh`.
La méthode implémentée est celle utilisant celle utilisant la librairie fld issue d'openCV.


```
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
```

- Le code s'appuie sur l'algorithme ```fld``` pour détecter les segments dans les images à partir desquels sont calculées les orientations de chacune des parcelles du RPG en entrée.

- Pour exécuter le code en parallèle, choisir ```--nb_cores```>1.

- Si la ou les images en entrée sont de grandes tailles, il est conseillé de définir une ```--patch_size``` qui sera utilisée pour réaliser un traitement par patch (plus rapide grâce à la parallélisation).

- Les fichiers ```--slope``` et ```--aspect``` doivent être générés au préalable (cf. *Calcul des données utilisées dans le calcul des orientations*) et fournis en entrée.


## Etapes de l'algorithme

Une fois les lignes détectées dans l'image (via pylsd ou fld), différents traitements sont appliqués sur les lignes afin de calculer l'orientation globale de la culture pour chaque parcelle.

Voici les grandes étapes de l'algorithme :


Pour chaque parcelle :

1. On récupère les lignes qui correspondent à la parcelle ;
2. Si le **nombre de lignes contenues dans une parcelle est inférieur à un nombre donné** (pour le moment fixé à 40), on ne sait pas donner l'orientation de la parcelle (trop incertaine) et on passe à la parcelle suivante. Sinon, on continue de travailler dans la parcelle actuelle :
3. Une ligne = un trait entre un point A=(xa, ya) et B=(xb,yb). Pour chaque ligne on calcule le vecteur AB = (xb-xa, yb-ya) qu'on normalise.
4. Une fois qu'on a toutes les coordonnées des vecteurs normalisés de la parcelle, on souhaite supprimer les outliers. On utilise pour cela l'indicateur **IQR = Q3 - Q1**, avec Q1 = 1er quartile et Q3 = 3ème quartile. La règle "standard" qui définie les outliers est la suivante : **les valeurs en dessous de Q1-1.5\*IQR ou au-dessus et Q3+1.5\*IQR sont considérées comme des outliers**. Si un vecteur normalisé possède une coordonnée en x ou en y identifiée comme outlier, il est supprimé de la liste des vecteurs.
5. La **norme des vecteurs restants est ensuite vérifiée : si elle est inférieure à un seuil donné (fixé ici à 8 pour la vigne), on ne prend pas en compte le vecteur**. On s'affranchit ainsi des petites lignes qui sont en bordure de parcelle et qui perturbent l'orientation globale.
6. Une fois tous les vecteurs de la parcelle triés, on fait la médiane des déplacements ce qui nous donne (xmed, ymed).
7. On calcule le centroide de la parcelle (xc, yc).
8. Le segment qui représente visuellement l'orientation de la vigne est centré sur le centroide et relie les points (xc-xmed, yc-ymed) et (xc+xmed, yc+ymed). Pour plus de visibilité (segments plus grands), un facteur A assez conséquent a été rajouté : (xc-A * xmed, yc-A * ymed) et (xc+A * xmed, yc+A * ymed).

On peut représenter ces différentes étapes sous forme de schéma :

<img src="imgs/shema_code_calcul_orientation.PNG"  width="900">


De plus pour chaque orientation calculée, 4 colonnes d'indicateurs de qualité sur l'orientation calculée ont été ajoutées :

- "NB_LINES" qui totalise le nombre de lignes détectées prises en compte dans le calcul de l'orientation (plus on a de lignes et plus l'orientation calculée est fiable) ;
- "MEAN_LINES" qui donne la longueur moyenne des lignes prises en compte (plus les lignes sont longues et plus on a de chances qu'elles soient pertinentes dans le calcul de l'orientation).
- Les colonnes "STD_X_COOR" et "STD_Y_COOR" qui donnent l'écart-type des coordonnées en x et en y des lignes normalisées.

A partir des rasters Aspect et Slope calculés auparavent on peut extraire la valeur moyenne des pixels de ces éléments pour chaque parcelle. Ces valeurs moyennes ont été ajoutées dans des colonnes du shapefile :
- "SLOPE" qui indique l'angle moyen de la pente en degrés ;
- "ASPECT" qui indique l'orientation moyenne de la pente en degrés (angle azimut).
- "CALC_ASPECT" qui est la conversion en angle azimut du vecteur calculé de l'orientation des cultures, afin d epouvoir comparer l'orientation de la pente avec celle des cultures.

Enfin une colonne "INDIC_ORIE" a été ajoutée ; il s'agit d'un indicatur d'orientation allant de 0 à 90. 0=les rangées des cultures sont dans le sens de la pente ; 90=les orientations sont perpendiculaires.

Computation of crop orientation
===============================

#Change installation procedure
#TO DO

Crop Orientation is a common theme across various projects.

------------------------------------
Code file contained in the directory
------------------------------------

- `detection_orientation_culture/orientation_detection.py`: Code to detect crop orientation using the Pylsd segment detection algorithm.
- `detection_orientation_culture/line_detection_lsdcmla.py` : Code for segment detection using the LSD CMLA algorithm.
- `detection_orientation_culture/detect_orientation_qsub.sh` : Qsub script to launch a job on the cluster for crop orientation detection using Pylsd.
- `detection_orientation_culture/lsd_cmla_qsub.sh` : Qsub script to launch a job on the cluster for line detection using the LSD CMLA algorithm.

Using Qsub scripts
==================

------------------------------------------
Computation of crop orientation with pylsd
------------------------------------------

To obtain the crop orientation in a shapefile format, you need to use the script `detect_orientation_qsub.sh`.

.. code-block:: console

    python orientation_detection.py --img path/to/image_file_or_directory
                                    --type extension_file_type
                                    --rpg path/to/rpg_file.shp \
                                    --out_shp path/to/output_file.shp \
                                    --out_csv path/to/output_file.csv \
                                    --nb_cores 12 \
                                    --patch_size 10000 \
                                    --slope path/to/slope_file.tif \
                                    --aspect path/to/aspect_file.tif


- The code relies on ```pylsd``` algorithm to detect segments in the images, from which the orientations of each plot in the input RPG are calculated.

- To run the code in parallel, set ```--nb_cores```>1.

- If the input image(s) are large, it is recommended to define a ```--patch_size``` to perform patch-based processing (which is faster thanks to parallelization).

- The extracted orientations will be stored in the ```--out_shp```

- The file ```--out_csv``` will contain a summary of the execution times and the number of detections.

- The files ```--slope``` and ```--aspect``` must be generated beforehand (see Calculation of data used for orientation calculation) and provided as input.

---------------------------------------------
Computation of crop orientation with LSD CMLA
---------------------------------------------

Extraction of lines in agricultural plots with the LSD CMLA algorithm
---------------------------------------------------------------------


With the script `lsd_cmla_qsub.sh`.

An example with a single input image:

.. code-block:: console

    python lsd_cmla.py --img /work/OT/eolab/DATA/BD_ORTHO/BDO_RVB_0M50_LAMB93_D11_2015.tif --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude_0M50_lsdcmla.shp


An example with a folder containing the input images:

.. code-block:: console

    python lsd_cmla.py --img /work/OT/eolab/DATA/BD_ORTHO/BDORTHO_2-0_RVB-0M50_JP2-E080_LAMB93_D011_2015-01-01/BDORTHO/1_DONNEES_LIVRAISON_2016-05-00226/BDO_RVB_0M50_JP2-E080_LAMB93_D11-2015 \
                        --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude_0M50_lsdcmla.shp \
                        --type jp2

You must specify the image file extension with the ```--type``` option.


Use of extracted lines to calculate crop orientation in plots
---------------------------------------------------------------------

**Merge of LSD CMLA shapefiles**

With QGIS `Vector -> Data Management Tool -> Merge Vector Layers`.

**Intersection between previous and RPG plots**

With QGIS `Vector -> Geoprocessing tools -> Intersection`.
The goal is to obtain LSD lines only within the RPG plots. The resulting shapefile of the lines must include a column containing the RPG plot IDs for the orientation calculation to work.

Orientation computing
---------------------

TO DO

Without Qsub scripts (unrecommended)
====================================

Warning: The conda environment of one is not compatible with that of the other. Therefore, you must use two separate terminal windows to run the different functions, unless the qsub scripts are used.

-------------------------------
Algorithm and conda environment
-------------------------------

This algorithm is based on the LineSegmentDetection (LSD) CMLA algorithm from OTB to detect lines in images. Then, various processing steps are applied to these lines to calculate the overall crop orientation for each plot.

Here are the steps of the algorithm:

.... TO DO

Extraction of lines in agricultural plots with the LSD CMLA algorithm
---------------------------------------------------------------------

**a. Conda environnement**

You must have the LSD CMLA module installed beforehand (the OTB base package only includes the standard LSD module, which is much less efficient). If needed, contact Yannick Tanguy for assistance with installation.

Once installed, it must be launched. For example, in my session, I follow these steps in a new terminal window:

.. code-block:: console

    cd /work/OT/eolab/guntzbp/build/LSD
    module load otb/7.0
    . ~/bin/envOTBapp.sh
    cd repertory/with/the/code/to/launch


**b. Function to launch**

This is done using the `lineSegmentDetection_CMLA()` function in the file `parcelle_orientation.py`.
The output is a shapefile containing the lines across the image. These lines will then be intersected with the plots in the next step, keeping only the lines that are inside the plots.

You need to modify the paths to the data (RPG, images, output shapefiles, etc.) as currently, they are hardcoded in the script.

Use of extracted lines to calculate crop orientation in plots
---------------------------------------------------------------------

**a. Conda environnement**

When using eolab :

.. code-block:: console

    module load conda
    conda activate /softs/projets/eolab/conda/eolab

**b. Function to launch**

First, you need to retrieve the information from the DEM (Digital Elevation Model) to obtain the average slope and the average orientation of the slope for each plot.
To create the monolithic DEM for a given department (in this case, department 11: Aude), use the `gdalbuildvrt` command:

.. code-block:: console

    gdalbuildvrt -a_srs EPSG:2154 RGE_ALTI_11_5m.vrt /work/datalake/static_aux/MNT/RGEALTI_5M_France/1_DONNEES_LIVRAISON_2020-04-00197/RGEALTI_MNT_5M_ASC_LAMB93_IGN69_D011/*.asc


You can then calculate the slope angle and the orientation of the slope into two rasters using `gdaldem` :

.. code-block:: console

    # gdaldem slope : gives the DTM slope value in degrees for each pixel
    gdaldem slope of GTiff RGE_ALTI_11_5m.vrt  RGE_ALTI_11_5m_SLOPE.tif

    # gdaldem aspect: gives the orientation value of the DTM slope in azimuth angle for each pixel (North = 0°, East = 90°, South = 180°, West = 270°).
    gdaldem aspect of GTiff RGE_ALTI_11_5m.vrt  RGE_ALTI_11_5m_ASPECT.tif

These rasters will be used in the final processing to calculate parcel orientation.

The final step before running the function that calculates the orientation of the plots is to compute the intersection between the lines detected by the LSD CMLA algorithm and the RPG. This step is essential. To do this, use the `intersection_RPG_lines()` of the file `parcelle_processing.py` ; the output of this function can be used as input for the final function `intersection_RPG_lines_polygone_per_polygon()`
 for the detected LSD CMLA lines parameter.

The last step involves using the `intersection_RPG_lines_polygone_per_polygon()` of the file `parcelle_processing.py` to calculate the crop orientation and the various indicators.
You need to modify the paths to the data (RPG, images, output shapefiles, etc.) as currently, they are hardcoded in the script.

This function combines the different steps to calculate the orientation for each crop plot:

For each plot:

1. Retrieve the lines that correspond to the plot;
2. If the **number of lines within a plot is below a given threshold** (currently set to 40), the orientation of the plot cannot be determined (too uncertain), and the next plot is processed. Otherwise, continue working with the current plot:
3. A line = a segment between a point A = (xa, ya) and B = (xb, yb). For each line, calculate the vector AB = (xb - xa, yb - ya) and normalize it.
4. Once all the coordinates of the normalized vectors for the plot are obtained, outliers need to be removed. The **IQR indicator = Q3 - Q1** is used, where Q1 is the first quartile and Q3 is the third quartile. The standard rule for identifying outliers is as follows: **values below Q1 - 1.5 * IQR or above Q3 + 1.5 * IQR are considered outliers**. If a normalized vector has an x or y coordinate identified as an outlier, it is removed from the list of vectors.
5. The **magnitude of the remaining vectors is then checked**: if it is below a given threshold (set here to 8 for vineyards), the vector is discarded. This helps eliminate small lines along the edges of the plot that could distort the overall orientation.
6. Once all the vectors for the plot are sorted, the median displacement is calculated, which gives us (xmed, ymed).
7. The centroid of the plot is computed (xc, yc).
8. The segment representing the visual orientation of the vineyard is centered on the centroid and connects the points (xc - xmed, yc - ymed) and (xc + xmed, yc + ymed). For better visibility (longer segments), a significant factor A is added: (xc - A * xmed, yc - A * ymed) and (xc + A * xmed, yc + A * ymed).

These steps can be represented in the form of a diagram:

<img src="imgs/shema_code_calcul_orientation.PNG"  width="900">

Additionally, for each calculated orientation, 4 quality indicator columns have been added for the computed orientation:

- "NB_LINES" which totals the number of detected lines considered in the orientation calculation (the more lines we have, the more reliable the calculated orientation is);
- "MEAN_LINES" which provides the average length of the lines considered (the longer the lines, the more likely they are relevant in the orientation calculation).
- The "STD_X_COOR" and "STD_Y_COOR" columns which give the standard deviation of the x and y coordinates of the normalized lines.

From the previously calculated Aspect and Slope rasters, we can extract the average pixel values of these elements for each plot. These average values have been added as columns in the shapefile:
- "SLOPE" which indicates the average slope angle in degrees;
- "ASPECT" which indicates the average orientation of the slope in degrees (azimuth angle).
- "CALC_ASPECT" which is the azimuth angle conversion of the calculated crop orientation vector, to compare the slope orientation with that of the crops.

Finally, a column "INDIC_ORIE" has been added; it is an orientation indicator ranging from 0 to 90. 0 = the crop rows follow the slope direction; 90 = the orientations are perpendicular.


---------------------------------------------------
Computation of data used in orientation computation
---------------------------------------------------

First, you need to retrieve the information from the DEM (Digital Elevation Model) to obtain the average slope and the average orientation of the slope for each plot.
To create the monolithic DEM for a given department (in this case, department 11: Aude), use the `gdalbuildvrt` command:

.. code-block:: console

    gdalbuildvrt -a_srs EPSG:2154 RGE_ALTI_11_5m.vrt /work/datalake/static_aux/MNT/RGEALTI_5M_France/1_DONNEES_LIVRAISON_2020-04-00197/RGEALTI_MNT_5M_ASC_LAMB93_IGN69_D011/*.asc

Then, you can calculate the slope angle and the slope orientation into two rasters using `gdaldem` :

.. code-block:: console

    # gdaldem slope : gives the slope value of the DEM in degrees for each pixel
    gdaldem slope of GTiff RGE_ALTI_11_5m.vrt  RGE_ALTI_11_5m_SLOPE.tif

    # gdaldem aspect: gives the slope orientation of the DEM in azimuth angle for each pixel (North = 0°, East = 90°, South = 180°, West = 270°).
    gdaldem aspect of GTiff RGE_ALTI_11_5m.vrt  RGE_ALTI_11_5m_ASPECT.tif

These rasters will be used in the final processing step to calculate the orientation of the plots.

