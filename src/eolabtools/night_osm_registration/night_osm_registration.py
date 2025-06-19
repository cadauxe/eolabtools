# -*- coding: utf-8 -*-
""" Night visible data registration based on OSM reference

:authors: see AUTHORS file
:organization: CNES
:copyright: CNES. All rights reserved.
:license: see LICENSE file
:created: 2024
"""

import os
import ssl
import getpass
import argparse
import warnings

import numpy as np

import pyrosm
import rasterio
from rasterio import features, mask
import shapely
from shapely.geometry import box
from skimage.morphology import binary_closing
import pyproj
import pandas as pd
import geopandas as gpd
import cv2
from math import *
from scipy import interpolate, ndimage
from utils import (otb_img_resample, crop_raster, remove_otb_path)

def cmd_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', dest='infile', type=str, help='Input radiance or multispectral image') 
    parser.add_argument('--outpath', dest='outpath', type=str, help='Output directory')
    parser.add_argument('--ws', dest='window_size', type=int, help='Size of the subtile sampling [px]')
    parser.add_argument('--ms', dest='max_shift', type=int, help='Limit value for valid shift computation [px]')
    parser.add_argument('--subsampl', dest='subsampling', type=int, help='Intermediate Subsampling to allow displacement grid interpolation at subtile edges [px]', required=False, default = 1)
    parser.add_argument('--rasterize', dest='rasterize', action = 'store_true', default = False, help='Indicate if rasterization of radiance/multispectral image is needed')
    parser.add_argument('--raster_bin', dest='raster_bin', type=str, help='If rasterize not required, binarized input image', required = False)  
    parser.add_argument('--raster_osm', dest='raster_osm', type=str, help='If rasterize not required, rasterized osm file to be used for shifts determination', required = False)
    parser.add_argument('--proxy', dest='proxy', type=str, help='If --rasterize and if the OSM reference download is needed through a proxy server : proxy server address (with the form : [proxy_address]:[port])', required = False)
    parser.add_argument('--city', dest='city_name', type=str, help='If --rasterize, name of the considered city for OSM retrieval', required = False)
    parser.add_argument('--osm_dir', dest='osm_dir', type=str, help='If --rasterize, output directory for osm data retrieval', required = False)
    parser.add_argument('--roi', dest='roi_file', type=str, help='If --rasterize, region of interest, shapefile format', required = False)
    parser.add_argument('--thr', dest='radiance_threshold', type=float, help='If --rasterize, radiance theshold for binarization', required = False, default = 10)
    parser.add_argument('--water', dest='water_shp', type=str, help='If --rasterize, shapefile defining water locations', required = False)
    # pb with osm water polygons (at least with pyrosm) - TODO : try with another library 
    # meanwhile : water polygons made with QuickOSM in QGIS
    # QuickOSM, request natural=water+water=river -> water-river layer
    # QuickOSM, request landuse = residential -> residential layer
    # layer islands = intersection(water-river, residential)
    # final water_layer = water_river - islands
    args = parser.parse_args()
    return args          


def raster_to_bin(raster: rasterio.io.DatasetReader, r: int = 0.2989, g: int = 0.5870, b: int = 0.1140, S: float = 10):
    """
    Build panchromatic raster from r, g, b bands and then apply binary closing
    :param raster: raster source
    :param: roi to crop the source
    :param r: red coefficient for panchromatic
    :param g: green coefficient for panchromatic
    :param b: blue coefficient for panchromatic
    :param S: threshold to binarize a radiance raster
    :return: raster binarized and eventually cropped
    """
 
    print("binarization of input raster")
    

    if len(raster.indexes)==1:
        # one band with radiance informationr
        raster_pan = raster.read(1) 
        raster_pan[raster_pan<=S] = 0
        raster_pan[raster_pan>S] = 1
 
    else:
        # Combine R, G, B bands to produce total radiance image
        raster_pan = r * raster.read(1) + g * raster.read(2) + b * raster.read(3)
        raster_pan[raster_pan<=S] = 0
        raster_pan[raster_pan>S] = 1
    
    raster_pan = np.uint8(raster_pan)

    # Binary closing  
    raster_bin = binary_closing(raster_pan)
    raster_bin = np.uint8(1 * raster_bin)

    return raster_bin


def get_osm_data(city_name: str, bbox: shapely.geometry.polygon.Polygon = None, epsg = None, download_dir=None, proxy = None, water_file=None):
    """
    Download osm data in vector format
    :param city_name: name of the city to download
    :param bbox: Shapely polygon defining area of interest
    :param download_dir: directory path to store download osm data
    :param proxy: proxy address
    :param water_file: external vector file with water features
    :return: geopandas osm vector data
    """
    print("get osm data")

    if proxy is not None:
        # Config Proxy
        u = getpass.getuser()
        p = getpass.getpass('Password : ')

        os.environ['HTTP_PROXY'] = "http://{}:{}@{}".format(u, p, proxy)
        os.environ['HTTPS_PROXY'] = "http://{}:{}@{}".format(u, p, proxy)
        ssl._create_default_https_context = ssl._create_unverified_context

    # Download OSM data
    # if the pbf file has previously been downloaded in the directory, it will be used and not updated.  
    fp = pyrosm.get_data(city_name, directory=download_dir)

    #reproject bbox in WGS84
    if (epsg != 'epsg:4326'):
        project = pyproj.Transformer.from_proj(pyproj.Proj(init=epsg), pyproj.Proj(init='epsg:4326'))
        bbox = shapely.ops.transform(project.transform, bbox)

    # Initialize the OSM parser object
    osm = pyrosm.OSM(fp, bounding_box=bbox)

    # Read water
    if water_file is None:
        gdf_water = osm.get_data_by_custom_criteria(custom_filter={'water':['river']})
    else:
        #get water features, ! should be in crs 4326
        gdf_water=gpd.read_file(water_file, bbox)


    # Read all buildings + cemetery + parks...
    landuses = ["cemetery", "forest", "meadow", "farmland", "quarry", "allotments"]
    naturals = ["wood"]
    leisures_negative = ["nature_reserve", "park", "garden", "golf_course"]
    historics = ["fort"]
    aeroways_negative = ["heliport", "aerodrome"]
    amenities = ["school"]
    sports = ["horse_racing", "equestrian"]

    print("get buildings")
    gdf_building = osm.get_buildings()
    print("get other negative features")
    gdf_other_negative = osm.get_data_by_custom_criteria(custom_filter={
                                                   'landuse' : landuses,
                                                   'natural' : naturals,
                                                   'leisure' : leisures_negative,
                                                   'historic' : historics, 
                                                   'aeroway' : aeroways_negative,
                                                   'amenity' : amenities,
                                                   'sport' : sports}, 
                                                    keep_nodes = False)


    gdf_negative = pd.concat([gdf_building, gdf_water, gdf_other_negative])
    # Read all bright objects to superimpose on black objects
    man_mades = ["bridge"]
    leisures_positive = ["pitch"]
    aeroways_positive = ["apron"]
    print("get other positive features")
    gdf_positive = osm.get_data_by_custom_criteria(custom_filter={
                                                   'man_made': man_mades,
                                                   'leisure' : leisures_positive,
                                                   'aeroway' : aeroways_positive},
                                                    keep_nodes = False)
    return gdf_negative, gdf_positive


def osm_vector_to_raster(raster, gdf_osm_negative, gdf_osm_positive, roi_list = []):
    """
    Rasterize vector osm data
    :param raster: raster which define targets (resolution, shape, transform)
    :param gdf_osm: geopandas osm vector
    :return: osm vector rasterized
    """
    print("binaryze osm vector")


    #TODO :prise en compte Emprise ROI (default 1, fill 0)
    if (len(roi_list) != 0):
        raster_roi = features.rasterize(roi_list,
                                        out_shape=raster.shape,
                                        fill=0,
                                        transform=raster.transform,
                                        all_touched=False,
                                        default_value=1,
                                        dtype=None)
    
    # Get list of geometries for all features in vector file - WGS84
    negative_geom_list = []
    for shapes in gdf_osm_negative.geometry:
        if (raster.crs != 'epsg:4326'):
            #reproject	
            project = pyproj.Transformer.from_proj(pyproj.Proj(init='epsg:4326'), pyproj.Proj(init=raster.crs))
            shapes = shapely.ops.transform(project.transform, shapes)                  
        negative_geom_list.append(shapes)    

    positive_geom_list = []
    for shapes in gdf_osm_positive.geometry:
        if (raster.crs != 'epsg:4326'):
            #reproject	
            project = pyproj.Transformer.from_proj(pyproj.Proj(init='epsg:4326'), pyproj.Proj(init=raster.crs))
            shapes = shapely.ops.transform(project.transform, shapes)            
        positive_geom_list.append(shapes) 

    # Rasterize
    raster_osm = features.rasterize(negative_geom_list,
                                    out_shape=raster.shape,
                                    fill=1,
                                    transform=raster.transform,
                                    all_touched=False,
                                    default_value=0,
                                    dtype=None)
    
    positive_raster_osm = features.rasterize(positive_geom_list,
                                    out_shape=raster.shape,
                                    fill=0,
                                    transform=raster.transform,
                                    all_touched=False,
                                    default_value=1,
                                    dtype=None)
    
    raster_osm[np.where(positive_raster_osm==1)] = 1


    if (len(roi_list) != 0):
        raster_osm[np.where(raster_roi==0)] = 0	 

    return raster_osm


def get_shift_via_fft(raster_a, raster_b):


    # Get the spectral constituents for image 1 and its complex conjugate for image 2:
    image1_fft = np.fft.fft2(raster_a)
    image2_fft = np.conjugate(np.fft.fft2(raster_b))

    # Now we can directly correlate the two images (spectral cross correlation):
    cross_corr = np.real(np.fft.ifft2((image1_fft * image2_fft)))

    # The cross correlation matrix is mirrored so we need to do a fftshift :
    cross_corr_shift = np.fft.fftshift(cross_corr)

    # Now we can look for the correlation with the maximum amplitude :
    row, col = raster_a.shape

    row_shift, col_shift = np.unravel_index(np.argmax(cross_corr_shift), (row, col))

    row_shift -= int(row / 2)
    col_shift -= int(col / 2)

    return -row_shift, -col_shift


def compute_shift(raster_a, raster_b, tile_size, max_shift_thr):

    shift_mask = np.zeros_like(raster_a, dtype='u1')
    filtered_shift_mask = np.zeros_like(raster_a, dtype='u1')
    
    n_row = ceil(raster_a.shape[0]/tile_size)
    n_col = ceil(raster_a.shape[1]/ tile_size)

    shift_row_pos = np.zeros((n_row, n_col), dtype=np.int64)
    shift_col_pos = np.zeros((n_row, n_col), dtype=np.int64)
    shift_row_val = np.zeros((n_row, n_col), dtype=np.int64)
    shift_col_val = np.zeros((n_row, n_col), dtype=np.int64)
    dt = np.dtype((np.int64, (4,)))
    tiles = np.empty((n_row, n_col), dtype=dt)
    print('compute shift for %i tiles' % (n_row * n_col))
    for i in range(n_row):
        for j in range(n_col):
            k = j + n_col * i
            print(i, j, "%i/%i" % (k, n_row * n_col))
            bounds = [i * tile_size,
                      j * tile_size,
                      min((i + 1) * tile_size, raster_a.shape[0]),
                      min((j + 1) * tile_size, raster_a.shape[1])
                      ]
            tile_a = raster_a[bounds[0]: bounds[2], bounds[1]: bounds[3]]
            tile_b = raster_b[bounds[0]: bounds[2], bounds[1]: bounds[3]]

            if np.all(tile_a == 0) or np.all(tile_b == 0):
                continue

            dec_li, dec_co = get_shift_via_fft(tile_a, tile_b)

            print("dec_li, dec_co before filtering", dec_li, dec_co)

            # d�placement du filtrage par rapport max-shift plus loin pour interpoler 
            #les valeurs selon les voisins plut�t que de supposer un d�placement nul
	    #if abs(dec_co) > max_shift_thr or abs(dec_li) > max_shift_thr:
            #    continue

            shift_row_pos[i, j] = bounds[0] + int((bounds[2] - bounds[0]) / 2)
            shift_col_pos[i, j] = bounds[1] + int((bounds[3] - bounds[1]) / 2)
            shift_row_val[i, j] = dec_li
            shift_col_val[i, j] = dec_co
            tiles[i, j] = bounds
	    # draw the shift in the mask
            startPoint = (shift_col_pos[i, j], shift_row_pos[i, j])
            endPoint = (shift_col_pos[i, j] + dec_co, shift_row_pos[i, j] + dec_li)

            if abs(dec_co) > max_shift_thr or abs(dec_li) > max_shift_thr:
                filtered_shift_mask = cv2.arrowedLine(filtered_shift_mask,startPoint,endPoint,1, 1)  
            else:
                shift_mask = cv2.arrowedLine(shift_mask,startPoint,endPoint,1, 1)      

    return shift_row_val, shift_col_val, shift_row_pos, shift_col_pos, tiles, shift_mask, filtered_shift_mask

def grid_hole_filling(src):
    
    nl = src.shape[0]
    nc = src.shape[1]
    # replace filtered value by mean of 3*3 window
    for i in range(nl):
        for j in range(nc):
            if np.isnan(src[i,j]):
                imin = max(i-1, 0) 
                imax = min(i+1, nl-1) 		 	
                jmin = max(j-1, 0)
                jmax = min(j+1, nc-1) 
                window = src[imin:imax+1,jmin:jmax+1]
                mean = np.nanmean(window) 		
                if np.isnan(mean):
                    mean = 0		
                src[i,j] = mean		

    return src

def compute_displacement_grid(shape, shift_row_val, shift_col_val, window_size, max_shift, subsampling):

    print("compute displacement grid")

    # outliers removal
    # Identify position where absolute values exceed a given threshold
    mask_row_shift = abs(shift_row_val) > max_shift
    mask_column_shift = abs(shift_col_val) > max_shift
    
    # Merge both masks to allow filtering to be applied to both shifts grids
    mask = mask_row_shift | mask_column_shift

    del mask_row_shift
    del mask_column_shift

    # Set Outliers to NaN in Displacements grids (remove shifts if line shift OR colum shift is higher than max_shift))  
    shift_row_val = shift_row_val.astype('float64')
    shift_col_val = shift_col_val.astype('float64')
    shift_row_val[np.where(mask == True)] = np.nan
    shift_col_val[np.where(mask == True)] = np.nan

    # mean to fill filtered values
    shift_row_val = grid_hole_filling(shift_row_val)
    shift_col_val = grid_hole_filling(shift_col_val)    

    # Shifts values Replication according to intermediate resolution
    # Such a step allows keeping central shift values at the center of
    # the subtiles to force interpolation at the subtiles edges ONLY!
    # subsampling = 1 -> interpolation on all the subtile
    #          -------------------------------------
    #          | Shift Interpolation Only at EdgeS |
    #          | h ----------------------------- h |
    #          | i |                           | i |
    #          | f |                           | f |
    #          | t |                           | t |
    #          |   |                           |   |
    #          | I |                           | I |
    #          | n |                           | n |
    #          | t |      Keep Unchanged       | t |
    #          | e |       Shift Values        | e |
    #          | r |                           | r |
    #          | p |                           | p |
    #          |   |                           |   |
    #          | E |                           | E |
    #          | d |                           | d |
    #          | g |                           | g |
    #          | e ----------------------------- e |
    #          | Shift Interpolation Only at EdgeS |
    #          -------------------------------------
    shift_row_val = np.kron(shift_row_val, np.ones((subsampling,subsampling)))
    shift_col_val = np.kron(shift_col_val, np.ones((subsampling,subsampling)))

    # Resize to Radiance image dimension with spline interpolation
    zoom_factor = window_size / subsampling
    shift_row_val = ndimage.zoom(shift_row_val, (zoom_factor,zoom_factor), order=3)
    shift_col_val = ndimage.zoom(shift_col_val, (zoom_factor,zoom_factor), order=3)

    (ys, xs) = shape
    # Resize Interpolated Grids to fit cropped radiance image dimensions
    shift_row_val = shift_row_val[np.arange(ys), :][:, np.arange(xs)]
    shift_col_val = shift_col_val[np.arange(ys), :][:, np.arange(xs)]

    #plt.imshow(shift_row_val)
    #plt.show()
    #plt.imshow(shift_col_val)
    #plt.show()
    
    # Displacement Grid (opposite sign shift to be compliant with OTB GridBasedImageResampling
    disp_grid = np.stack((-shift_col_val,-shift_row_val), axis=0)
    del shift_col_val
    del shift_row_val
    # Round disp_grid to ensure relevant int type format
    disp_grid = (np.round(disp_grid)).astype('int16')
    return disp_grid


def run(path_image_de_nuit, path_out, window_size, max_shift, subsampling, rasterization = False, proxy = None, city_name = None, path_osm = None, path_water= None, roi_file = None, path_raster_osm = None, radiance_threshold = 10, path_raster_bin = None):

    raster_src = rasterio.open(path_image_de_nuit)

    if rasterization:
        """
        1. Transform night raster into binary raster
        """
        roi_list = []
        raster_src, raster_src_crs, raster_src_dtype, raster_src_shape, raster_src_transform = crop_raster(path_out, raster_src,
                                                                                               roi_file, roi_list)

        raster_bin, raster_osm = night_raster_to_bin(city_name, path_osm, path_out, path_water, proxy,
                                                     radiance_threshold, raster_src, raster_src_crs, raster_src_shape,
                                                     raster_src_transform, roi_list)
    else:
        raster_src, raster_src_crs, raster_src_dtype, raster_src_shape, raster_src_transform = crop_raster(path_out,
                                                                                                           raster_src,
                                                                                                           None,
                                                                                                           None)
        raster_bin = rasterio.open(path_raster_bin).read(1)
        raster_osm = rasterio.open(path_raster_osm).read(1)	   

    """
    3. Compute colocalisation error between raster and osm locally for each tile
    """
    shift_row_val, shift_col_val, shift_row_pos, shift_col_pos, tiles, shift_mask, filtered_shift_mask = compute_shift(raster_a=raster_bin,
                                                                               raster_b=raster_osm,
                                                                               tile_size=window_size, max_shift_thr = max_shift)
    del raster_bin, raster_osm

    # Check & Create Shift result folder
    out_ext = "/Shifts_WS" + str(window_size) + "px/"
    path_out_shift = path_out + out_ext
    if not os.path.exists(path_out_shift):
        os.makedirs(path_out_shift) 
	
    with rasterio.open(path_out_shift + "shift_mask.tif", mode="w",driver="GTiff", height=raster_src_shape[0], width=raster_src_shape[1], count=1, dtype=shift_mask.dtype, transform=raster_src_transform, crs=raster_src_crs) as new_dataset:
            new_dataset.write(shift_mask, 1)
	    
    with rasterio.open(path_out_shift + "filtered_shift_mask_MS"+str(max_shift)+"px.tif", mode="w",driver="GTiff", height=raster_src_shape[0], width=raster_src_shape[1], count=1, dtype=shift_mask.dtype, transform=raster_src_transform, crs=raster_src_crs) as new_dataset:
            new_dataset.write(filtered_shift_mask, 1)

    del shift_mask, filtered_shift_mask
	    
    #  Save np array and Plot Quiver
    np.savetxt(path_out_shift + "Decalage_en_ligne_valeur.csv", shift_row_val, fmt='%i', delimiter=",")
    np.savetxt(path_out_shift + "Decalage_en_colonne_valeur.csv", shift_col_val, fmt='%i', delimiter=",")
    np.savetxt(path_out_shift + "Decalage_en_ligne_position.csv", shift_row_pos, fmt='%i', delimiter=",")
    np.savetxt(path_out_shift + "Decalage_en_colonne_position.csv", shift_col_pos, fmt='%i', delimiter=",")

    del shift_row_pos, shift_col_pos
   
    """
    4. Compute displacement grid (size of raster_src)
    """
    disp_grid = compute_displacement_grid(raster_src_shape, shift_row_val, shift_col_val, window_size, max_shift, subsampling) 

    del shift_row_val, shift_col_val

    with rasterio.open(path_out_shift + "DisplacementGrid_MS"+ str(max_shift) + "px_SubS"+ str(subsampling) + ".tif", mode="w",driver="GTiff", height=raster_src_shape[0], width=raster_src_shape[1], count=2, dtype='int16', nodata = -9999.0, transform=raster_src_transform, crs=raster_src_crs) as new_dataset:
            new_dataset.write(disp_grid)
      
    """
    5. Apply Shift on the cropped image via OTB GridBasedImageResampling. If the input image is RGB, the shifted output is in total radiance
    """

    # OTB GridBasedImageResampling needs input without transform information (for both input image and grid)
    otb_input_path = path_out + "/OTB_input_raster.tif"
    otb_displacementgrid_path = path_out_shift + "OTB_DisplacementGrid_MS"+ str(max_shift) + "px_SubS"+ str(subsampling) + ".tif"
    otb_output_path = path_out_shift + "OTB_shifted_cropped_raster.tif"
    with rasterio.open(otb_displacementgrid_path, mode="w",driver="GTiff", height=raster_src_shape[0], width=raster_src_shape[1], count=2, dtype='int16', nodata = -9999.0, crs=raster_src_crs) as new_dataset:
            new_dataset.write(disp_grid)

    with rasterio.open(otb_input_path, mode="w",driver="GTiff", height=raster_src_shape[0], width=raster_src_shape[1], count=1, dtype=raster_src_dtype, crs=raster_src_crs) as new_dataset:
            new_dataset.write(raster_src.read(1),1)

    del disp_grid, raster_src

    otb_img_resample(otb_displacementgrid_path, otb_input_path, otb_output_path, raster_src_shape)

    otb_shifted_cropped_raster = (rasterio.open(otb_output_path)).read(1)
    with rasterio.open(path_out_shift + "shifted_cropped_raster_MS"+ str(max_shift) + "px_SubS"+ str(subsampling) + ".tif", mode="w",driver="GTiff", height=raster_src_shape[0], width=raster_src_shape[1], count=1, dtype=raster_src_dtype, transform=raster_src_transform, crs=raster_src_crs) as new_dataset:
            new_dataset.write(otb_shifted_cropped_raster,1) 

    del otb_shifted_cropped_raster
    remove_otb_path(otb_displacementgrid_path, otb_input_path, otb_output_path)

def night_raster_to_bin(city_name, path_osm, path_out, path_water, proxy, radiance_threshold, raster_src,
                        raster_src_crs, raster_src_shape, raster_src_transform, roi_list):
    raster_bin = raster_to_bin(raster=raster_src, S=radiance_threshold)
    with rasterio.open(path_out + "/raster_bin.tif", mode="w", driver="GTiff", height=raster_src_shape[0],
                       width=raster_src_shape[1], count=1, dtype=raster_bin.dtype, transform=raster_src_transform,
                       crs=raster_src_crs) as new_dataset:
        new_dataset.write(raster_bin, 1)
    """
        2. Get OSM building vector data and convert it to raster
        """
    vector_osm_negative, vector_osm_positive = get_osm_data(city_name=city_name, bbox=box(*raster_src.bounds),
                                                            epsg=raster_src_crs, download_dir=path_osm, proxy=proxy,
                                                            water_file=path_water)
    raster_osm = osm_vector_to_raster(raster_src, vector_osm_negative, vector_osm_positive, roi_list)
    del vector_osm_negative, vector_osm_positive
    with rasterio.open(path_out + "/raster_osm.tif", mode="w", driver="GTiff", height=raster_src_shape[0],
                       width=raster_src_shape[1], count=1, dtype=raster_osm.dtype, transform=raster_src_transform,
                       crs=raster_src_crs) as new_dataset:
        new_dataset.write(raster_osm, 1)
    return raster_bin, raster_osm


if __name__ == '__main__':

    args = cmd_parser()

    # Manage FutureWarnings from proj
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if args.rasterize == True:
        run(args.infile, args.outpath, args.window_size, args.max_shift, args.subsampling, rasterization = args.rasterize, proxy = args.proxy, city_name = args.city_name, path_osm = args.osm_dir, path_water = args.water_shp, roi_file = args.roi_file, radiance_threshold = args.radiance_threshold)
    else:
        run(args.infile, args.outpath, args.window_size, args.max_shift, args.subsampling, path_raster_osm = args.raster_osm, path_raster_bin = args.raster_bin)  


