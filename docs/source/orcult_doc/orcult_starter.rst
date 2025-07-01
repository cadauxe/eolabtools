.. _orcult_starter:

================
Getting Started
================

Crop orientation is a theme common to several projects. The idea is to calculate the crop orientation vector for each plot of interest.


Single tool installation procedure
===============================

To install DetectionOrientationCulture, please launch the following commands :

.. code-block:: console

    conda create -n orcult_env python=3.10 libgdal=3.11.0 -c conda-forge -c defaults -y
    conda activate orcult_env
    pip install eolabtools[DetecOrCult]

Generate the data used to compute orientations
===============================

First, we need to retrieve the information from the DTM to obtain the average slope and average slope orientation for each plot.
This step is performed using the `generate_slope_aspect.sh` script and is divided into several sub-tasks:

To create the monolithic DTM for a given department (here 11: Aude), use the `gdalbuildvrt` command:

.. code-block:: console

    gdalbuildvrt -a_srs EPSG:2154 RGE_ALTI_11_5m.vrt /work/datalake/static_aux/MNT/RGEALTI_5M_France/1_DONNEES_LIVRAISON_2020-04-00197/RGEALTI_MNT_5M_ASC_LAMB93_IGN69_D011/*.asc


You can then calculate the slope angle and the orientation of the slope into two rasters using `gdaldem` :

.. code-block:: console

    # gdaldem slope : gives the DTM slope value in degrees for each pixel
    gdaldem slope of GTiff RGE_ALTI_11_5m.vrt  RGE_ALTI_11_5m_SLOPE.tif

    # gdaldem aspect: gives the orientation value of the DTM slope in azimuth angle for each pixel (North = 0°, East = 90°, South = 180°, West = 270°).
    gdaldem aspect of GTiff RGE_ALTI_11_5m.vrt  RGE_ALTI_11_5m_ASPECT.tif

These rasters will be used in the final processing to calculate parcel orientation.


Code file contained in the directory
===============================

- `detection_orientation_culture/orientation_detection.py`: Code to detect crop orientation using the Pylsd segment detection algorithm.
- `detection_orientation_culture/detect_orientation_qsub.sh` : Qsub script to launch a job on the cluster for crop orientation detection using Pylsd.



Launching the computation of crop orientation with fld
===============================

To obtain the crop orientation in a shapefile format, please use the following command. More examples are provided in the script
`detect_orientation_qsub.sh`. The method implemented uses the fld library from openCV.

.. code-block:: python

    detection_orientation_culture --img path/to/image_file_or_directory
                                  --type extension_file_type
                                  --rpg path/to/rpg_file.shp \
                                  --out_shp path/to/output_file.shp \
                                  --out_csv path/to/output_file.csv \
                                  --nb_cores 12 \
                                  --patch_size 10000 \
                                  --slope path/to/slope_file.tif \
                                  --aspect path/to/aspect_file.tif


- The code relies on the fld algorithm to detect the segments in the images from which the orientations of each of the input RPG
plots are calculated.

- To run the code in parallel, select `--nb_cores`>1.

- If the input image(s) is (are) large, it is advisable to define a --patch_size which will be used to perform patch processing
(faster thanks to parallelization).

- The `--slope` and `--aspect` files must be generated beforehand (see Calculating data used in orientation calculations) and
supplied as input.


Steps of the algorithm
===============================

Once the lines have been detected in the image (via pylsd or fld), various treatments are applied to the lines to calculate the overall crop orientation for each plot.

Here are the main steps in the algorithm:

For each plot:

1. **Segment detection :** Retrieve the lines that correspond to the plot;
2. **Filtering:** If the number of lines within a plot is below a given threshold (currently set to 20), the orientation of the plot cannot be determined (too uncertain), and the next plot is processed. Otherwise, continue working with the current plot.
3. **Check direction :** If all segments are all in same direction, go to step 4, else we do:
    - **Segment clustering :** Segments that are in the same direction are assigned to the same cluster.
    - **Plot subdivision :** Following the number of cluster defined in the previous step, the original plot is refined to smaller ones based on the cluster segement counts. And each of the new smaller plots follow individually the next steps

These steps can be represented in the form of a diagram:

.. figure:: /_static/orcult/overall_scheme.png
   :alt:
   :width: 70.0%
   :align: center

Then the orientation is computed in 5 steps :

1. **Vector normalization :** A line = a segment between a point A = (xa, ya) and B = (xb, yb). For each line, calculate the vector AB = (xb - xa, yb - ya) and normalize it.
2. **Outliers detection :** Once all the coordinates of the normalized vectors for the plot are obtained, outliers need to be removed. The IQR indicator = Q3 - Q1 is used, where Q1 is the first quartile and Q3 is the third quartile. The standard rule for identifying outliers is as follows: values below Q1 - 1.5 * IQR or above Q3 + 1.5 * IQR are considered outliers. If a normalized vector has an x or y coordinate identified as an outlier, it is removed from the list of vectors.
3. **Magnitude check :** The magnitude of the remaining vectors is then checked: if it is below a given threshold (set here to 8 meters for vineyards), the vector is discarded. This helps eliminate small lines along the edges of the plot that could distort the overall orientation.
4. **Centroid computation :** Once all the vectors for the plot are sorted, the median displacement is calculated, which gives us (xmed, ymed) and of the plot's centroid (xc, yc).
5. **Line extension :** The segment representing the visual orientation of the vineyard is centered on the centroid and connects the points (xc - xmed, yc - ymed) and (xc + xmed, yc + ymed). For better visual outcome (longer segments recovering the whole plot), a significant factors A and A' is added: (xc - A * xmed, yc - A * ymed) and (xc + A' * xmed, yc + A' * ymed) in order to extend the orientation line to the plot's edges.

.. figure:: /_static/orcult/orientation_computation.png
   :alt:
   :width: 70.0%
   :align: center

Additionally, for each calculated orientation, 4 quality indicator columns have been added for the computed orientation:

- "NB_LINES" which totals the number of detected lines considered in the orientation calculation (the more lines we have, the more reliable the calculated orientation is);
- "MEAN_LINES" which provides the average length of the lines considered (the longer the lines, the more likely they are relevant in the orientation calculation).
- The "STD_X_COOR" and "STD_Y_COOR" columns which give the standard deviation of the x and y coordinates of the normalized lines.

From the previously calculated Aspect and Slope rasters, we can extract the average pixel values of these elements for each plot. These average values have been added as columns in the shapefile:
- "SLOPE" which indicates the average slope angle in degrees;
- "ASPECT" which indicates the average orientation of the slope in degrees (azimuth angle).
- "CALC_ASPECT" which is the azimuth angle conversion of the calculated crop orientation vector, to compare the slope orientation with that of the crops.

Finally, a column "INDIC_ORIE" has been added; it is an orientation indicator ranging from 0 to 90. 0 = the crop rows follow the slope direction; 90 = the orientations are perpendicular.

