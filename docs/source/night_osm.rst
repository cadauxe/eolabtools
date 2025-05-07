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


# Night visible data registration based on OSM reference

## Installation

First install the Orfeo ToolBox.
Then use venv or uv to create a virtual environment, follow the [OTB docs](https://www.orfeo-toolbox.org/CookBook-develop/Installation.html#create-an-healthy-python-environment-for-otb) to create an healthy venv with compiled python bindings.

Then install the module in your venv:

```bash
source venv/bin/activate
pip install .
# Or use "editable" mode to be albe to modify code without reinstall
pip install -e .
```

## Principle

A city seen from above at night can be compared to a city map.

Input of the algorithm: A single-band or RGB image. In the second case case, the algorithm computes the total radiance via a composition of RGB bands.

Main steps of the algorithm :

1. Radiance image thresholding and binarization.
2. Extraction of OpenStreetMap layers (buildings, streets, bridges, highways...) and binarization. The resulting OSM raster should be as close as possible to the binarized input image.
3. Tiling of the two rasters and computation of a row and column offset for each tile using spectral cross correlation.
4. Computation of a global registration grid with the same geometry as the input file by interpolation of the shift values of each tile. It is possible to keep the shift values at the center of the subtiles and force the interpolation at the subtile edges or to interpolate on all the subtile.
5. Application of the grid on the radiance image.

## Configs

### Main configuration file

A main configuration file is needed to run the tool. A template is available [here](configs/config.yml).

### OSM extraction

OSM layer extraction is handle by a configuration file.
See two examples with [simple](configs/osm_config_simple.yml) and [subtracted](configs/osm_config_subtracted.yml) methods.

Simple: road vectors are simply rasterized (small memory footprint)
Subtracted: everything else is rasterized and subtracted to obtain roads (huge memory footprint)

## Commands

### night_osm_image_registration

The installation will create the command `night_osm_image_registration` that takes the following argument :

- `infile`: reference input image to compute shift grid
- `auxfiles`: optional list of additional images to shift based on the same grid
- `-o`, `--outdir`: output files location
- `--config`: path to the main configuration file
- `--osm-config`: path to the OSM configuration file with tags to keep in binary raster

```bash
mkdir /tmp/output/
cp configs/config.yml /tmp/output/my_config.yml
# Modify the config file, then run the script
night_osm_image_registration -o /tmp/my_output/ --config /tmp/output/my_config.yml --osm-config configs/osm_config_simple.yml radiance.tif [ another_image.tif ]
```

#### Outputs

`XXXX` being the reference image:

- `XXXX_cropped.tif` : radiance raster cropped to the ROI
- `XXXX_binary.tif` : binarized cropped input raster
- `XXXX_osm.tif` : binarized OSM raster with same extent as input image

In a directory `XXXX_MS_WS_SS/` (MS=max shift, WS=windows size, SS=sub sampling) :

- `<image_basename>_shifted.tif` : input ref or aux image shifted in x and y using `displacement_grid.tif`. Band 1 of the displacement grid corresponds to X shift, and band 2 to Y shift.
- `decalage_en_colonne/ligne_position/valeur.csv` : value and position (center of subtile) of shifts before MS filtering.
- `shift_mask.tif` : mask with a shift arrow in the center of each subtile before filtering
- `filtered_shift_mask.tif` : mask with a shift arrow in the center of each subtile after filtering

### night_osm_vector_registration

The command `night_osm_vector_registration` allows to apply the displacement grid on vectors (only geom type "Point" is handled for now).

Arguments are the following :

- `invector` : Path to the input vector file.
- `grid` : Path to the displacement grid (band1 : shift along X in pixels, band 2 : shift along Y in pixels).
- `-o`, `--outdir` : Output directory.
- `-n`, `--name` : Basename for the output file.

```bash
night_osm_vector_registration -o /tmp/output/ -n test_shift my_points.gpkg displacement_grid.tif
```

## Advices

### Dataset not available in pyrosm

If chosen `city_name` is not directly available in pyrosm, you can download the OSM "Protocolbuffer Binary Format" file (.pbf) you need in the free [Geofabrik](https://download.geofabrik.de) server. As the minimum distribution level for these files is the region, you can use the [Osmium](https://osmcode.org/osmium-tool/index.html) library to crop the .pbf file in the desired zone. Once [installation](https://osmcode.org/osmium-tool/manual.html) is done, you can use the following command:

```bash
osmium extract -p zone.geojson region.osm.pbf -o zone.osm.pbf
```

- `zone.geojson` contains the poligon defining the zone to crop. Must be a geojson file.
- `region.osm.pbf` is the .pbf file downloaded from Geofabrik server.
- `zone.osm.pbf` is the output path of the cropped .pbf file.

### Water shapefile

By default, an extraction of water osm layers is done with pyrosm, however the result is not satisfactory.
A better water layer can be computed with the following procedure using QuickOSM in QGIS:

1. QuickOSM : get a water-river layer with the request `natural=water + water=river`.
2. QuickOSM : get a residential layer with the request `landuse = residential`
3. Compute a islands layer = intersection(water-river, residential). May need to clean manually polygons.
4. Compute a layer river = water_river - islands.
5. Compute the final water layer as : (natural = water) - water_river + river.
