.. _night_osm:

======================
Night OSM Registration
======================

This tool performs night visible data registration based on OSM reference.

Single tool installation procedure
===============================

To install NightOsmRegistration, please launch the following commands :

.. code-block:: console

    conda create -n nightosm_env python=3.11 libgdal=3.11.0 markupsafe -c conda-forge
    conda activate nightosm_env
    pip install eolabtools[NightOsmReg]


Steps of the algorithm
======================

A city seen from above at night can be compared to a city map.

Here are the main steps of the algorithm :

- Radiance image thresholding and binarization.

- Extraction of OpenStreetMap layers (buildings, streets, bridges...) and binarization.

The resulting OSM raster should be as close as possible to the binarized input image.

- Tiling of the two rasters and computation of a row and column offset for each tile using spectral cross correlation.

- Computation of a global registration grid with the same geometry as the input file by interpolation of the shift values of
each tile. It is possible to keep the shift values at the center of the subtiles and force the interpolation at the subtile edges
or to interpolate on all the subtiles.

- Application of the grid on the radiance image.


Input files and configuration
==========================


Input of the algorithm: a RGB image or an image with total radiance information. In the first case, the algorithm computes the
total radiance via a composition of RGB bands.

A main configuration file is needed to run the tool. A template is available here.

DOWNLOAD config example and add them as hyperlinks

OSM extraction
OSM layer extraction is handle by a configuration file.
See two examples with simple and subtracted methods.
Simple: road vectors are simply rasterized (small memory footprint)
Subtracted: everything else is rasterized and subtracted to obtain roads (huge memory footprint)

Using night_osm_image_registration
==================================

Command line
------------

Use the command ``night_osm_image_registration`` with the following arguments :

.. code-block:: console

    night_osm_image_registration radiance.tif [another_image.tif]
                                 -o /tmp/my_output/
                                 --config /tmp/output/my_config.yml
                                 --osm-config configs/osm_config_simple.yml


- **``infile`` :** reference input image to compute shift grid

- **``auxfiles`` :** optional list of additional images to shift based on the same grid

- **``-o``, ``--outdir`` :** output files location

- **``--config`` :** path to the main configuration file

- **``--osm-config`` :** path to the OSM configuration file with tags to keep in binary raster

Output files
------------

XXXX being the reference image:


``XXXX_cropped.tif`` : Radiance raster cropped to the ROI

``XXXX_binary.tif`` : Binarized cropped input raster

``XXXX_osm.tif`` : Binarized OSM raster with same extent as input image

In a directory `XXXX_MS_WS_SS/` (MS=max shift, WS=windows size, SS=sub sampling) :


``<image_basename>_shifted.tif`` : Input ref or aux image shifted in x and y using displacement_grid.tif. Band 1 of the displacement grid corresponds to X shift, and band 2 to Y shift.

``decalage_en_colonne/ligne_position/valeur.csv`` : Value and position (center of subtile) of shifts before MS filtering.

``shift_mask.tif`` : Mask with a shift arrow in the center of each subtile before filtering

``filtered_shift_mask.tif`` : Mask with a shift arrow in the center of each subtile after filtering


Using night_osm_vector_registration
==================================

Command line
------------

Use the command ``night_osm_vector_registration`` with the following arguments :

.. code-block:: console

    night_osm_vector_registration my_points.gpkg
                                  displacement_grid.tif
                                  -o /tmp/output/
                                  -n test_shift


Arguments are the following :

- **``invector`` :** Path to the input vector file.

- **``grid`` :** Path to the displacement grid (band1 : shift along X in pixels, band 2 : shift along Y in pixels).

- **``-o``, ``--outdir`` :** Output directory.

- **``-n``, ``--name`` :** Basename for the output file.

Output files
------------

TO FILL

Advices
=======

Dataset not available in pyrosm
-------------------------------

If chosen city_name is not directly available in pyrosm, you can download the OSM "Protocolbuffer Binary Format" file (.pbf)
you need in the free `Geofabrik server <https://download.geofabrik.de/>`_. As the minimum distribution level for these files is
the region, you can use the `Osmium <https://osmcode.org/osmium-tool/index.html>`_
library to crop the .pbf file in the desired zone. Once `Osmium installation <https://osmcode.org/osmium-tool/manual.html>`_
is done, you can use the following command:

.. code-block:: console

    osmium extract -p zone.geojson region.osm.pbf -o zone.osm.pbf


- `zone.geojson` contains the polygon defining the zone to crop. Must be a geojson file.

- `region.osm.pbf` is the .pbf file downloaded from Geofabrik server.

- `zone.osm.pbf` is the output path of the cropped .pbf file.


Water shapefile
---------------

By default, an extraction of water osm layers is done with pyrosm, however the result is not satisfactory.
A better water layer can be computed with the following procedure using QuickOSM in QGIS:

- QuickOSM : get a water-river layer with the request ``natural=water + water=river``.

- QuickOSM : get a residential layer with the request ``landuse = residential``

- Compute a islands layer = intersection(water-river, residential). May need to clean manually polygons.

- Compute a layer ``river = water_river - islands``.

- Compute the final water layer as : ``(natural = water) - water_river + river``.
