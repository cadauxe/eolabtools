.. _detect_cult:

=============================
Detection Orientation Culture
=============================


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

