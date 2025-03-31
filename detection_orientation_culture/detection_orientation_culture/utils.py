import os
import time
from typing import Dict, List, Tuple

import geopandas as gpd
import pandas as pd
import git
import numpy as np
import numpy.linalg as la
import rasterio
import shapely
from rasterstats import zonal_stats
from scipy.stats import iqr

from sklearn.neighbors import BallTree


def get_nearest(src_points, candidates, k_neighbors=1):
    """Find nearest neighbors for all source points from a set of candidate points"""

    # Create tree from the candidate points
    tree = BallTree(candidates, leaf_size=15, metric='haversine')

    # Find closest points and distances
    distances, indices = tree.query(src_points, k=k_neighbors)

    # Transpose to get distances and indices into arrays
    distances = distances.transpose()
    indices = indices.transpose()

    # Get closest indices and distances (i.e. array at index 0)
    # note: for the second closest points, you would take index 1, etc.
    closest = indices[0]
    closest_dist = distances[0]

    # Return indices and distances
    return (closest, closest_dist)


def azimuth_angles_with_railroad(left_gdf, right_gdf):
    """
    For each point in left_gdf, find closest point in right GeoDataFrame and return them.

    NOTICE: Assumes that the input Points are in WGS84 projection (lat/lon).
    """

    left_geom_col = left_gdf.geometry.name
    right_geom_col = right_gdf.geometry.name

    # Ensure that index in right gdf is formed of sequential numbers
    right = right_gdf.copy().reset_index(drop=True)

    splitted = []
    for geom in right.geometry:
        if geom.__class__ == shapely.geometry.LineString:
            splitted += [shapely.geometry.LineString([geom.coords[i], geom.coords[i+1]]) for i in range(len(geom.coords)-1)]
        elif geom.__class__ == shapely.geometry.MultiLineString:
            for l in geom:
                splitted += [shapely.geometry.LineString([l.coords[i], l.coords[i+1]]) for i in range(len(l.coords)-1)]

    right = gpd.GeoDataFrame({"geometry": splitted})

    # Parse coordinates from points and insert them into a numpy array as RADIANS
    left_radians = np.array(left_gdf[left_geom_col].apply(lambda geom: (geom.centroid.x * np.pi / 180, geom.centroid.y * np.pi / 180)).to_list())
    right_radians = np.array(right[right_geom_col].apply(lambda geom: (geom.centroid.x * np.pi / 180, geom.centroid.y * np.pi / 180)).to_list())

    # Find the nearest points
    # -----------------------
    # closest ==> index in right_gdf that corresponds to the closest point
    # dist ==> distance between the nearest neighbors (in meters)

    closest, _ = get_nearest(src_points=left_radians, candidates=right_radians)

    # Return points from right GeoDataFrame that are closest to points in left GeoDataFrame
    closest_lines = right.loc[closest]

    # Ensure that the index corresponds the one in left_gdf
    closest_lines = closest_lines.reset_index(drop=True)

    orient = pd.Series(left_gdf.geometry.to_list())
    closest_lines = pd.Series(closest_lines.geometry.to_list())

    angles = orient.combine(closest_lines, compute_angles)

    return angles


def compute_angles(l_left, l_right):
        v1 = l_left.coords
        v2 = l_right.coords

        v1 = np.array([v1[1][0] - v1[0][0], v1[1][1] - v1[0][1]])
        v2 = np.array([v2[1][0] - v2[0][0], v2[1][1] - v2[0][1]])
        cosang = np.dot(v1, v2)
        sinang = la.norm(np.cross(v1, v2))
        angle = np.degrees(np.arctan2(sinang, cosang))

        if angle > 90:
            return 180 - angle
        else:
            return angle


def get_commit_hash() -> str:
    repository = git.Repo(search_parent_directories=True)
    sha = repository.head.object.hexsha

    return sha


def normalize_img(img, mask) -> np.array:
    """
        This method extracts red green and blue channels from
        the input image and convert them to 8 byte images.
        It is the one to use as it does not take the nodata into account while computing the percentiles
    """
    bands = []
    for c in range(img.shape[0]):
        band = img[c, :, :]
        masked_band = np.ma.masked_where(band == 0, band).compressed()
        percentile_3 = np.percentile(masked_band, 2)
        percentile_97 = np.percentile(masked_band, 98)
        clipped_band = np.clip(img[c, :, :], percentile_3, percentile_97)
        norm_band = ((clipped_band - percentile_3) / (percentile_97 - percentile_3)) * 255
        norm_band = np.where(mask, np.clip(norm_band, 1, 255), 0)

        bands.append(norm_band)

    return np.dstack(tuple(bands))


def create_linestring(seg, transform, width_reduction) -> Dict[shapely.geometry.linestring.LineString, float]:
    """
        Create a shapely.geometry.linestring.LineString given a rasterio.transform
    """
    pt1 = rasterio.transform.xy(
        transform,
        int(seg[1]),
        int(seg[0]),
    )
    pt2 = rasterio.transform.xy(
        transform, 
        int(seg[3]), 
        int(seg[2])
    )
    width = seg[4]

    l1 = shapely.geometry.shape({"type": "LineString", "coordinates": [pt1, pt2]})
    if not l1.is_valid:
        print("Error computing LineString. Faulty : ", l1, pt1, pt2)

    return {"geometry": l1, "width": width * width_reduction}


def get_norm_linestring(ls: shapely.geometry.linestring.LineString) -> Tuple[float, float, float, shapely.geometry.linestring.LineString]:
    """
        Compute the norm of the input segment
        
        Parameters
        ----------
        ls: the input LineString

        Returns
        -------
        norm: the norm of the input LineString
        nx: the normalized x coordinate
        ny: the normalized y coordinate
        ls: the input linestring
    """

    if ls.type == "MultiLineString":
        coord = ls[0].coords
    else :
        coord = ls.coords
    coord = ls.coords
    x1 = coord[0][0]
    y1 = coord[0][1]
    x2 = coord[1][0]
    y2 = coord[1][1]
    # to get the coordinates in the same direction we set x1 to be the
    if x2 < x1 :
        x1_bp = x1
        x2_bp = x2
        y1_bp = y1
        y2_bp = y2
        x1 = x2_bp
        y1 = y2_bp
        x2 = x1_bp
        y2 = y1_bp
    # then normalising them : |P1P2|=sqrt((x2-x1)^2 +(y2-y1)^2)
    norm = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    if norm != 0:
        nx = (x2 - x1) / norm
        ny = (y2 - y1) / norm
        return norm, nx, ny, ls
    else:
        return norm, 0, 0, None


def get_mean_slope_aspect(
    pol: shapely.geometry.polygon.Polygon, 
    slope: str, 
    aspect: str, 
    time_slope_aspect
):
    """
        Get mean slope and aspect for the input parcel
        
        Parameters
        ----------
        pol: the input Polygon
        slope: the path to the slope file
        aspect: the path to the aspect file
        time_slope_aspect: variable shared between processes to track process time

        Returns
        -------
        value_mean_slope: the mean slope for the parcel
        value_mean_aspect: the mean aspect for the parcel
    """

    if 'PROJ_LIB' in os.environ:
        del os.environ['PROJ_LIB']

    start_slope_aspect = time.process_time()

    value_mean_slope = zonal_stats(pol, slope, stats='mean')[0]['mean']
    value_mean_aspect = zonal_stats(pol, aspect, stats='mean')[0]['mean']

    end_slope_aspect = time.process_time() - start_slope_aspect
    time_slope_aspect.set(time_slope_aspect.value + end_slope_aspect)

    return value_mean_slope, value_mean_aspect


def filter_segments(segments: gpd.GeoDataFrame, min_len_line: float):
    """
        Filter input segments using quantiles and the input minimum length

        Parameters
        ----------
        segments: GeoDataframe containing the LineStrings
        min_len_line: the minimum length for the segments

        Returns
        -------
        vectx: the normalized x coordinates
        vecty: the normalized y coordinates
        len_lines: the lengths of the segments
        kept_lines: the filtered LineStrings
    """

    df_norm_vectxy = segments.geometry.apply(get_norm_linestring)
    
    vectx = [e[1] for e in df_norm_vectxy.to_list()]
    vecty = [e[2] for e in df_norm_vectxy.to_list()]
    # X
    iqr_x = iqr(vectx, axis=0)
    Q1_x = np.quantile(vectx, 0.25)
    Q3_x = np.quantile(vectx, 0.75)
    min_outlier_x = Q1_x - 1.5 * iqr_x
    max_outlier_x = Q3_x + 1.5 * iqr_x
    # Y
    iqr_y = iqr(vecty, axis=0)
    Q1_y = np.quantile(vecty, 0.25)
    Q3_y = np.quantile(vecty, 0.75)
    min_outlier_y = Q1_y - 1.5 * iqr_y
    max_outlier_y = Q3_y + 1.5 * iqr_y

    interval = 0
    list_filtered = list(filter(lambda t: t[1] > (min_outlier_x - interval) and \
            t[1] < (max_outlier_x + interval) and \
            t[2] > (min_outlier_y - interval) and \
            t[2] < (max_outlier_y + interval) and \
            t[0] > min_len_line, df_norm_vectxy.to_list()))

    # continues only if there are lines kept in the list (at least 2 to compute statistics)
    len_lines = [e[0] for e in list_filtered]
    vectx = [e[1] for e in list_filtered]
    vecty = [e[2] for e in list_filtered]
    kept_lines = [e[3] for e in list_filtered]

    return vectx, vecty, len_lines, kept_lines


def split_img_dataset(
    img_path: str, 
    RPG: gpd.GeoDataFrame, 
    patch_size: int, 
    list_rpg_patches, 
    time_split
):
    """
        Append the patches to the list of patches for the parallelized processes.
        
        Parameters
        ----------
        img_path: the input image path
        RPG: the input RPG
        patch_size: the size to use to create the list of rasterio.windows.Window to read the image
        list_rpg_patches: the list of Tuples containing image path, RPG within the window, and the Window
        time_split: variable shared between processes to track process time
    """

    start_split = time.process_time()

    with rasterio.open(img_path) as dataset:
        if patch_size:
            num_rows, num_cols = dataset.shape
            src_transform = dataset.transform
            dataset_bb = shapely.geometry.box(*dataset.bounds)

            windows = [rasterio.windows.Window(i, j, min(num_rows-i, patch_size), min(num_cols-j, patch_size))
                for i in range(0, num_rows, patch_size) for j in range(0, num_cols, patch_size)]

            for window in windows:
                bb = shapely.geometry.box(*rasterio.windows.bounds(window, src_transform))
                intersects = RPG.intersects(bb)
                within = RPG.within(dataset_bb)

                if (intersects & within).any():
                    list_rpg_patches.append((img_path, RPG.loc[intersects & within], window))

        else:
            bb = shapely.geometry.box(*dataset.bounds)
            intersects = RPG.intersects(bb)
            if intersects.any():
                list_rpg_patches.append((img_path, RPG.loc[intersects], None))

    time_split.set(time_split.value + time.process_time() - start_split)


def split_img_borders(
    img_path: str, 
    RPG: gpd.GeoDataFrame, 
    patch_size: int, 
    list_on_border, 
    time_split
):
    """
        Append the border patches to the list of border patches for the parallelized processes.
        
        Parameters
        ----------
        img_path: the input image path
        RPG: the input RPG
        patch_size: the size to use to create the list of rasterio.windows.Window to read the image
        list_on_border: the list of Tuples containing image path, RPG within the window, and the Window
        time_split: variable shared between processes to track process time
    """
    start_split = time.process_time()

    with rasterio.open(img_path) as dataset:
        num_rows, num_cols = dataset.shape
        src_transform = dataset.transform
        dataset_bb = shapely.geometry.box(*dataset.bounds)

    windows = [rasterio.windows.Window(i, j, min(num_rows-i, patch_size), min(num_cols-j, patch_size))
        for i in range(0, num_rows, patch_size) for j in range(0, num_cols, patch_size)] if patch_size else None

    # Get the polygons intersected by but not within the image extent ie on the image borders
    border_dataset = RPG.intersects(dataset_bb) & ~RPG.within(dataset_bb)
    if windows:
        for i,window in enumerate(windows):
            window_bb = shapely.geometry.box(*rasterio.windows.bounds(window, src_transform))
            intersects = RPG.intersects(window_bb)

            # Get the polygons that are both on the image borders and the window
            border =  border_dataset & intersects
            if border.any():
                rpg = RPG.loc[border]
                list_on_border.append((img_path, rpg, window))

    else:
        if border_dataset.any():
            list_on_border.append((img_path, RPG.loc[border_dataset], None))

    time_split.set(time_split.value + time.process_time() - start_split)


def split_windows(
    window: rasterio.windows.Window, 
    img_path: str, 
    RPG: gpd.GeoDataFrame, 
    list_rpg_patches, 
    time_split
):
    """
        Append the border patches to the list of border patches for the parallelized processes.
        
        Parameters
        ----------
        img_path: the input image path
        RPG: the input RPG
        windows: the list of rasterio.windows.Window
        list_on_border: the list of Tuples containing image path, RPG within the window, and the Window
        time_split: variable shared between processes to track process time
    """

    start_split = time.process_time()

    with rasterio.open(img_path) as dataset:
        dataset_bb = shapely.geometry.box(*dataset.bounds)
        src_transform = dataset.transform

    bb = shapely.geometry.box(*rasterio.windows.bounds(window, src_transform))
    intersects = RPG.intersects(bb)
    within = RPG.within(dataset_bb)

    if (intersects & within).any():
        list_rpg_patches.append((img_path, RPG.loc[intersects & within], window))
    
    time_split.set(time_split.value + time.process_time() - start_split)
