.. _night_osm:

======================
Night OSM Registration
======================

#Change installation procedure
#TO DO

Night visible data registration based on OSM reference (city context)

Principle
=========


A city seen from above at night can be compared to a city map.

Input of the algorithm: a RGB image or an image with total radiance information. In the first case, the algorithm computes the total radiance via a composition of RGB bands.

Main steps of the algorithm :

1. Radiance image thresholding and binarization.
2. Extraction of OpenStreetMap layers (buildings, streets, bridges...) and binarization. The resulting OSM raster should be as close as possible to the binarized input image.
3. Tiling of the two rasters and computation of a row and column offset for each tile using spectral cross correlation.
4. Computation of a global registration grid with the same geometry as the input file by interpolation of the shift values of each tile. It is possible to keep the shift values at the center of the subtiles and force the interpolation at the subtile edges or to interpolate on all the subtile.
5. Application of the grid on the radiance image.


Dependencies
============

Cf. requirements.txt

otbApplication

Command
=======


Use the command ``night_osm_registration.py`` with the following arguments :

``--infile`` path of the input image (can be either a RGB image or a radiance image).

``--outpath`` path to the output directory.

``--ws`` window size in pixels. Size of the subtiles.

``--ms`` max shift in pixels. Registration offsets beyond this threshold will be filtered.

``[--subsampl]`` subsampling, default = 1. Interpolation parameter in step 4. If 1, interpolation is done over the complete subtile.

``[--rasterize]`` If unset the first and second steps are passed. In that case the binarized input image and binarized osm raster must be given as input.

``[--raster_bin]`` path to the binarized imput image.

``[--raster_osm]`` path to the binarized osm raster.

``[--proxy]`` Proxy server address to be set for the OSM layers donwload during step 2 ([proxy address]:[port]).

``[--city]`` name of the city for OSM data retrieval.

``[--osm_dir]`` path to the output directory for OSM data retrieval, or path to the input directory containing OSM data if a new download is not required.

``[--roi]`` region of interest (in shapefile format). If rasterization is set, the input image will be cropped to this ROI. The ROI should contain a margin equivalent to the window size so that the registration offset calculated on the borders is correct.

``[--thr]`` radiance threshold, float, default = 10. Threshold used for the radiance image binarization.

``[--water]`` used in step 2 to define the water locations (in shapefile format). By default, an extraction of water osm layers is done with pyrosm, however the result is not satisfactory. A better water layer can be computed with the following procedure using QuickOSM in QGIS :

QuickOSM : get a water-river layer with the request ``natural=water + water=river``.

QuickOSM : get a residential layer with the request ``landuse = residential``

Compute a islands layer = intersection(water-river, residential). May need to clean manually polygons.

Compute  a layer river = water_river - islands.

Compute the final water layer as : (natural = water) - water_river + river.


Output
======

`cropped_raster.tif` : radiance raster cropped to the ROI

`raster_bin.tif` : binarized cropped input raster

`raster_osm.tif` : binarized OSM raster

In a directory `Shifts_WSxx` (WS for Window Size) :

`shifted_cropped_raster_MSxx_SubSxx.tif` : the input raster shifted in x and y according to the `DisplacementGrid_MSxx_SubSxx.tif` (MS for Max Shift and SubS for subsampling). Band 1 of the displacement grid corresponds to X shift, and band 2 to Y shift.

`decalage_en_colonne/ligne_position/valeur.csv` : value and position (center of subtile) of shifts before MS filtering.

`shift_mask.tif` : mask with a shift arrow in the center of each subtile before filtering

`filtered_shift_mask_MSxx.tif` : mask with a shift arrow in the center of each subtile after filtering


Tool
====

`apply_vector_registration.py` allows to apply the displacement grid on vectors (only geometry of type Point is handled for the moment). Arguments are the following :

`--invector` : Path to the input vector file.

`--grid` : Path to the displacement grid (band1 : shift along X in pixels, band 2 : shift along Y in pixels.

`--outpath` : Output directory.

`--name` : Basename for the output file.


