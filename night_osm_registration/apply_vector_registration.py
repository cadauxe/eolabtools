# -- coding: utf-8 --
""" Apply a displacement grid on a shapefile (geometry of type Point)

:authors: see AUTHORS file
:organization: CNES
:copyright: CNES. All rights reserved.
:license: see LICENSE file
:created: 23 October 2024
"""

import os
import argparse
import warnings

import rasterio
from rasterio import features
import shapely
import pyproj
import geopandas as gpd


def cmd_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--invector', dest='invector', type=str, help='Path to the input vector file') 
    parser.add_argument('--grid', dest='grid', type=str, help='Path to the displacement grid (band1 : shift along X in pixels, band 2 : shift along Y in pixels')
    parser.add_argument('--outpath', dest='outpath', type=str, help='Output directory')
    parser.add_argument('--name', dest='name', type=str, help='Basename for the output file')
    args = parser.parse_args()
    return args          



def run(vector_file, grid, path_out, basename):

    vectors = gpd.read_file(vector_file)
    
    grid = rasterio.open(grid)
    xgrid = grid.read(1)
    ygrid = grid.read(2)
 
    if vectors is not None:
        shapes_list = []
        for shape in vectors.geometry:
            if (vectors.crs != grid.crs):
		#reproject	
                project = pyproj.Transformer.from_proj(pyproj.Proj(init=vectors.crs), pyproj.Proj(init=grid.crs))
                shape = shapely.ops.transform(project.transform, shape)                            

            if shape.geom_type == 'Point':
                # indexes of the point in the grid
                row, col = grid.index(shape.x, shape.y)

		#values of shift in pixels
                xshift_px = xgrid[row, col]
                yshift_px = ygrid[row, col]

                # shift of the indexes
                shifted_col = col - xshift_px		
                shifted_row = row - yshift_px

                #coordinates of the shifted position
                shifted_x, shifted_y = grid.xy(shifted_row , shifted_col)
                shape = shapely.set_coordinates(shape, (shifted_x, shifted_y))									           
               		
            else :
                print("Only geometry of type Point is dealt with.")	    
	
            shapes_list.append(shape) 
    
        vectors.set_geometry(shapes_list, inplace = True)    
        vectors.to_file(path_out+"/"+basename+'.shp')
	
if __name__ == '__main__':

    args = cmd_parser()

    # Manage FutureWarnings from proj
    warnings.simplefilter(action='ignore', category=FutureWarning)

    run(args.invector, args.grid, args.outpath, args.name)

