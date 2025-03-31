import argparse
import concurrent.futures
import csv
import glob
import math
import os
import statistics
import time
from datetime import datetime
from functools import partial
from multiprocessing import Manager
from typing import Dict, List, Tuple

import geopandas as gpd
import git
import numpy as np
import numpy.linalg as la
import pandas as pd
import rasterio
import rasterio.mask
import shapely
from pylsd import lsd
from rasterio.plot import reshape_as_image, reshape_as_raster
from rasterio.windows import Window
from rasterstats import zonal_stats
from scipy.stats import iqr
from shapely.geometry import (LineString, MultiLineString, Point, Polygon, box,
                              shape)

from utils import (azimuth_angles_with_railroad, compute_angles,
                   create_linestring, filter_segments, get_commit_hash,
                   get_mean_slope_aspect, get_norm_linestring, normalize_img,
                   split_img_borders, split_img_dataset, split_windows)


def detect_multiple_orientations(
    lsd_lines: List[LineString],
    vectx: List[float],
    vecty: List[float],
    len_lines: List[float],
    orientation: LineString,
    min_nb_line_per_parcelle: int
):
    """
        Detect if a parcel contains multiple orientations and compute these orientations

        Parameters
        ----------
        lsd_lines: list of detected segments of one parcel
        vectx: the normalized x coordinates of the segments
        vecty: the normalized y coordinates of the segments
        len_lines: the lengths of the segments
        orientation: the orientation computed using the segments
        min_nb_line_per_parcelle: the minimum number of segments needed to compute a parcel's orientation

        Returns
        -------
        int
            the number of detected orientations
        dict
            a dictionnary containing:
            - the orientations
            - their centroids
            - the average length of the segments
            - the number of segments used 
            - the std of the segments x coordinates 
            - the std of the segments y coordinates
    """

    pd_lines = pd.DataFrame(lsd_lines)

    angles = pd_lines.applymap(partial(compute_angles, l_right=orientation))
    angles = angles.to_numpy().reshape(-1)
    # We compute the angles histogram and count the peaks ie the clusters of segments
    hist, bins = np.histogram(angles, bins=90//10, range=(0, 90))
    num_orient = len(hist[hist > min_nb_line_per_parcelle])

    if num_orient < 2:
        return num_orient, None

    print(f"Multiple orientations found: {num_orient}")
    upper_bounds = bins[1:][hist > min_nb_line_per_parcelle]

    # We keep only the top 3 clusters of segments
    sorted_idx = np.argsort(hist[hist > min_nb_line_per_parcelle])[::-1]
    topk_idx = sorted_idx[:min(3, len(sorted_idx))]

    orient_dict = {"orientations": [], "centroids": [], "mean_len_lines": [
    ], "nb_lines_used": [], "std_orient_x": [], "std_orient_y": []}
    for k in topk_idx:

        # Get the segments idx of the cluster
        ind_pseudo = (upper_bounds[k] - 10 <= angles) * \
            (angles <= upper_bounds[k])
        vectx_pseudo = np.array(vectx)[ind_pseudo]
        vecty_pseudo = np.array(vecty)[ind_pseudo]
        len_lines_pseudo = np.array(len_lines)[ind_pseudo]

        lsd_lines_pseudo = []
        for i in range(len(ind_pseudo)):
            if ind_pseudo[i]:
                lsd_lines_pseudo.append(lsd_lines[i])

        # Compute statistics
        mean_len_lines = statistics.mean(len_lines_pseudo)
        nb_lines_used = len(vectx_pseudo)
        std_orient_x = statistics.stdev(vectx_pseudo)
        std_orient_y = statistics.stdev(vecty_pseudo)

        xmed = statistics.median(vectx_pseudo)
        ymed = statistics.median(vecty_pseudo)

        # Get the "pseudo" parcel using the cluster of segments convex hull
        pseudo_parcel = MultiLineString(list(lsd_lines_pseudo)).convex_hull
        centroid = pseudo_parcel.centroid

        # Coordinates of the pseudo parcels centroid
        xc = centroid.x
        yc = centroid.y

        # to get bigger lines, we can use the bounds of the pseudo parcel :
        av = (pseudo_parcel.bounds[2] - pseudo_parcel.bounds[0]) / \
            4 + (pseudo_parcel.bounds[3] - pseudo_parcel.bounds[1]) / 4

        # to have a minimum length of the line orientation :
        min_length_orientation = 40
        if av >= min_length_orientation:
            pseudo_orient = LineString(
                [((xc - xmed * av), (yc - ymed * av)), ((xc + xmed * av), (yc + ymed * av))])
        else:
            pseudo_orient = LineString([((xc - xmed * min_length_orientation), (yc - ymed * min_length_orientation)),
                                       ((xc + xmed * min_length_orientation), (yc + ymed * min_length_orientation))])

        orient_dict["orientations"].append(pseudo_orient)
        orient_dict["centroids"].append(centroid)
        orient_dict["mean_len_lines"].append(mean_len_lines)
        orient_dict["nb_lines_used"].append(nb_lines_used)
        orient_dict["std_orient_x"].append(std_orient_x)
        orient_dict["std_orient_y"].append(std_orient_y)

    return len(topk_idx), orient_dict


def orientation_from_lines(
    vectx: List[float],
    vecty: List[float],
    pol: Polygon,
    value_mean_aspect: float
) -> Tuple[LineString, float, float]:
    """
    Extract global orientation from detected lines,
    calculate the azimuth angle associated,
    and the angle between the slope and the orientation.

    Parameters
    ---------- 
        vectx: x coordinates of the detected lines
        vecty: y coordinates of the detected lines
        pol: the RPG polygon
        value_mean_aspect

    Returns
    -------
        LineString
            the computed orientation
        float
            value_calc_aspect
        float
            indic_orient
    """

    # Calculating the median value of x and y  :
    # we have the median vector ie the median orientation of the parcel, Pmed=(xmed, ymed)
    xmed = statistics.median(vectx)
    ymed = statistics.median(vecty)
    # Coordinates of the centroid of the polygon
    xc = pol.centroid.x
    yc = pol.centroid.y

    # to get bigger lines, we can use the bounds of the polygon :
    av = (pol.bounds[2] - pol.bounds[0]) / 4 + \
        (pol.bounds[3] - pol.bounds[1]) / 4

    # to have a minimum length of the line orientation :
    min_length_orientation = 40
    if av >= min_length_orientation:
        final_linestrings_orientation = LineString(
            [((xc - xmed * av), (yc - ymed * av)), ((xc + xmed * av), (yc + ymed * av))])
    else:
        final_linestrings_orientation = LineString([((xc - xmed * min_length_orientation), (yc - ymed * min_length_orientation)), ((
            xc + xmed * min_length_orientation), (yc + ymed * min_length_orientation))])

    # convert the computed orientation vector into azimuth angle
    value_calc_aspect = 180 + math.degrees(math.atan2(xmed, ymed))

    # compute the indicator between the orientation of the plot and the slope orientation (both are in azimut angle)
    # 0 = plot orientation is in the same direction as the slope ; 90 = orientation is perpendicular to the direction of the slope.
    # 2nd version : is working as well, faster
    relativ_angle = (360 - value_mean_aspect +
                     value_calc_aspect) % 180  # modulo 180
    # the indicator is computed
    indic_orient = relativ_angle if relativ_angle <= 90 else 180 - relativ_angle

    return final_linestrings_orientation, value_calc_aspect, indic_orient


def compute_orientation(
    ind: int,
    RPG: gpd.GeoDataFrame,
    LSD: gpd.GeoDataFrame,
    slope: str,
    aspect: str,
    window_bb: shapely.geometry.box,
    area_min: float,
    parcel_ids_processed: list,
    min_nb_line_per_parcelle: int,
    min_len_line: float,
    time_slope_aspect: float,
    time_calculate_orientation: float,
    verbose: bool
):
    """
    Extract the orientation(s) of the parcel from detected lines,
    calculate the azimuth angle associated,
    and the angle between the slope and the orientation.

    Parameters
    ---------- 
        ind: the index of the parcel in the RPG
        RPG: the GeoDataFrame containing the parcels
        LSD: the GeoDataFrame containing the detected segments
        slope: the path to the slope file
        aspect: the path to the aspect file
        windows_bb: the window's bounding box
        area_min: a parameter used to calculate the minimum number of lines needed to compute the orientation of a parcel in relation to its area
        parcel_ids_processed: a list containing the ids of the parcel already handled
        min_nb_line_per_parcelle: the minimum number of lines needed to compute the orientation of a parcel
        min_len_line: the minimum length of a segment to be used in the orientation calculation
        time_slope_aspect: variable shared between processes to track process time
        time_slope_aspect: variable shared between processes to track process time
        verbose: boolean indicating whether or not to print all messages

    Returns
    -------
        list
            a list containing the computed orientation(s)
        list
            a list containing the computed centroid(s)
        str
            CODE_GROUP
        str
            CODE_CULTU
        list
            a list containing the number of lines used to compute each orientation
        int
            the number of orientations detected
        list
            a list containing the average lengths of the segments used to compute each orientation
        list 
            a list containing the std of the segments x coordinates used to compute each orientation
        list
            a list containing the std of the segments y coordinates used to compute each orientation
        float
            value_mean_slope
        float
            value_mean_aspect
        float
            value_calc_aspect
        float
            indic_orient
        str
            the id of the parcel
        list
            a list of LineString that where used to compute the orientation(s)
    """

    delta_calculate_orientation = time.process_time()

    # Get the parcel polygon
    pol = RPG.at[ind, "geometry"]
    centroid = [pol.centroid]

    # Get the id of the parcel
    ID_PARCEL = RPG.at[ind, "ID_PARCEL"]

    # Check if the parcel is not fully within the patch
    processed = ID_PARCEL in parcel_ids_processed

    # Check if the parcel has already been processed
    if processed:
        if verbose:
            print(f"Skipping parcel {ID_PARCEL}: already processed")
        return

    # Erode the polygon edges to filter out the segments on the border
    # The erosion is proportional to the parcel's area
    erosion = - 5 * np.max([1, np.log((pol.area / area_min)**2)])
    within = LSD.within(pol.buffer(erosion))
    inter = LSD.loc[within]

    # Check if any segment where detected in the polygon
    if inter.shape[0] < 1:
        if verbose:
            print(
                f"Skipping parcel {ID_PARCEL}: no segment to compute the parcel orientation")
        return

    # Check if the parcel is fully within the windows bounds
    # if window_bb.contains(pol):
        # Store the id of the parcel in the list shared between processes to avoid redundancies
    parcel_ids_processed.append(ID_PARCEL)

    code_group = RPG.at[ind, "CODE_GROUP"]
    code_cultu = RPG.at[ind, "CODE_CULTU"]

    # compute mean value of slope and aspect with zonal_stats
    value_mean_slope, value_mean_aspect = get_mean_slope_aspect(
        pol, slope, aspect, time_slope_aspect)

    if value_mean_aspect is None or value_mean_slope is None:
        if verbose:
            print(
                f"Skipping parcel {ID_PARCEL}: mean slope value={value_mean_slope}, mean aspect value={value_mean_aspect}")
        return

    # Filter the segments
    vectx, vecty, len_lines, kept_lines = filter_segments(inter, min_len_line)

    if len(vectx) <= (min_nb_line_per_parcelle * np.max([1, pol.area / area_min])):
        if verbose:
            print(
                f"Skipping parcel {ID_PARCEL}: not enough segments kept to compute the parcel orientation")
        return

    # Compute orientation
    orientation, value_calc_aspect, indic_orient = orientation_from_lines(
        vectx,
        vecty,
        pol,
        value_mean_aspect
    )

    # computes statistics for quality criteria
    mean_len_lines = [statistics.mean(len_lines)]
    nb_lines_used = [len(vectx)]
    std_orient_x = [statistics.stdev(vectx)]
    std_orient_y = [statistics.stdev(vecty)]

    nb_orientations, orient_dict = detect_multiple_orientations(
        kept_lines, vectx, vecty, len_lines, orientation, min_nb_line_per_parcelle)

    if orient_dict is not None:
        orientation = orient_dict["orientations"]
        centroid = orient_dict["centroids"]
        mean_len_lines = orient_dict["mean_len_lines"]
        nb_lines_used = orient_dict["nb_lines_used"]
        std_orient_x = orient_dict["std_orient_x"]
        std_orient_y = orient_dict["std_orient_y"]
    else:
        orientation = [orientation]

    delta_calculate_orientation = time.process_time() - delta_calculate_orientation
    time_calculate_orientation.set(
        time_calculate_orientation.value + delta_calculate_orientation)
    return orientation, centroid, code_group, code_cultu, nb_lines_used, nb_orientations, mean_len_lines, std_orient_x, std_orient_y, value_mean_slope, value_mean_aspect, value_calc_aspect, indic_orient, ID_PARCEL, kept_lines


def orientation_worker(
    data: Tuple[str, gpd.GeoDataFrame, Window],
    normalize: bool,
    parcel_ids_processed: list,
    lsd_params: dict,
    slope: str,
    aspect: str,
    area_min: float,
    time_inter_mask_open: float,
    time_slope_aspect: float,
    time_lsd: float,
    time_orientation_worker: float,
    time_calculate_orientation: float,
    save_lsd: bool,
    verbose: bool
) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Apply the lsd algorithm to the input image and compute the crop orientations for the parcels in the RPG.

    Parameters
    ----------
        data: a tuple containing the input image path, the rpg parcels, and an optionnal rasterio.Window with which to read the image
        normalize: boolean indicating whether or not the image has to be normalized 
        parcel_ids_processed: a list (shared between all the worker instances) containing the already processed parcels ids
        lsd_params: params for lsd segment detection
        slope: the path to the raster containing the slope values
        aspect: the path to the raster containing the aspect values
        time_inter_mask_open: shared variable to track process time to open, intersect with RPG and mask the image
        time_slope_aspect: shared variable to track process time to compute slope and aspect
        time_lsd: shared variable to track process time to detect segments with LSD algorithm
        time_orientation_worker: shared variable to track process time to compute the orientations
        time_calculate_orientation: shared variable to track process time to calculate each orientation
        save_lsd: bool indicating whether or not the segments used to compute the orientations have to be saved in file
        verbose: boolean indicating whether or not to print all messages

    Returns
    -------
        gpd.GeoDataFrame
            a gpd.GeoDataFrame containing the orientations
        gpd.GeoDataFrame
            a gpd.GeoDataFrame containing the centroids
        gpd.GeoDataFrame
            a gpd.GeoDataFrame containing the segments used to compute the orientations
    """

    start = time.process_time()

    img_path, rpg, window = data

    with rasterio.open(img_path) as dataset:
        print(f"Patch {os.path.basename(img_path)} ({window})...", end="")

        # Get the polygons intersected by the window and add expansion
        dataset_bb = box(*dataset.bounds)
        rpg_expanded = rpg.buffer(1).intersection(dataset_bb)

        # Get new window
        src_transform = dataset.transform
        win_transform = rasterio.windows.transform(window, src_transform)
        window_bb = box(*rasterio.windows.bounds(window, src_transform))
        # Check if the new window is not too big
        if box(*rpg_expanded.total_bounds).area < window_bb.area * 3:
            window = rasterio.windows.from_bounds(
                *rpg_expanded.total_bounds, src_transform)
            win_transform = rasterio.windows.transform(window, src_transform)
        else:
            rpg_expanded = rpg.buffer(1).intersection(window_bb)

        profile = dataset.profile
        mask_dataset = dataset.read_masks(1, window=window)
        crs = dataset.crs

        img = dataset.read(window=window)

    if normalize:
        img = normalize_img(img, mask_dataset)

    # Mask with RPG and dataset mask
    mask_rpg = rasterio.features.rasterize(list(rpg_expanded),
                                           out_shape=img.shape[1:],
                                           transform=win_transform,
                                           fill=0,
                                           all_touched=True,
                                           dtype=rasterio.uint8)
    img = np.uint8(img)
    img = np.where(mask_dataset*mask_rpg, img, 0)

    if window is not None:
        profile.data["width"] = window.width
        profile.data["height"] = window.height
        profile.data["transform"] = win_transform
        profile.data["dtype"] = "uint8"

    # image monobande en entree de pyLSD
    img = np.mean(img[0:3], axis=0)

    end_time_inter_mask_open = time.process_time() - start
    time_inter_mask_open.set(
        time_inter_mask_open.value + end_time_inter_mask_open)

    # Detect segments with LSD
    start_time_lsd = time.process_time()
    segments = lsd(
        np.asarray(img),
        scale=lsd_params["scale"],
        sigma_scale=lsd_params["sigma_scale"],
        quant=lsd_params["quant"],
        ang_th=lsd_params["ang_th"],
        eps=lsd_params["eps"],
        density_th=lsd_params["density_th"],
        n_bins=lsd_params["n_bins"])

    segments = list(map(partial(
        create_linestring,
        transform=profile["transform"],
        width_reduction=lsd_params["width_reduction"]),
        segments
    ))

    LSD = gpd.GeoDataFrame(segments, crs=crs)
    LSD.crs = rpg.crs

    lsd_dur = time.process_time() - start_time_lsd
    time_lsd.set(time_lsd.value + lsd_dur)

    orientations = []
    centroids = []
    list_code_group = []
    list_code_cultu = []
    nb_lines_used = []
    nb_orientations = []
    mean_len_lines = []
    std_orientation_x = []
    std_orientation_y = []
    mean_slope_list = []
    mean_aspect_list = []
    calc_aspect = []
    indic_orient = []
    list_ID_PARCEL = []
    kept_lines = []
    ID_PARCEL_kept_lines = []
    # Compute orientations from the detected segments
    for ind in list(rpg.index):
        r = compute_orientation(
            ind,
            rpg,
            LSD,
            slope,
            aspect,
            window_bb,
            area_min,
            parcel_ids_processed,
            lsd_params["min_nb_line_per_parcelle"],
            lsd_params["min_len_line"],
            time_slope_aspect,
            time_calculate_orientation,
            verbose
        )

        if r is not None:
            orientations += r[0]
            centroids += r[1]
            list_code_group += [r[2]] * len(r[0])
            list_code_cultu += [r[3]] * len(r[0])
            nb_lines_used += r[4]
            nb_orientations += [r[5]] * len(r[0])
            mean_len_lines += r[6]
            std_orientation_x += r[7]
            std_orientation_y += r[8]
            mean_slope_list += [r[9]] * len(r[0])
            mean_aspect_list += [r[10]] * len(r[0])
            calc_aspect += [r[11]] * len(r[0])
            indic_orient += [r[12]] * len(r[0])
            list_ID_PARCEL += [r[13]] * len(r[0])
            kept_lines += r[14]
            ID_PARCEL_kept_lines += [r[13]] * len(r[14])

    # Export and save the centroids
    centroids = gpd.GeoDataFrame({"geometry": centroids})
    centroids['CODE_GROUP'] = list_code_group
    centroids['CODE_CULTU'] = list_code_cultu
    centroids.crs = rpg.crs

    # Export and save the final linestring orientations
    orientations = gpd.GeoDataFrame(
        MultiLineString(orientations), columns=['geometry'])
    orientations['CODE_GROUP'] = list_code_group
    orientations['CODE_CULTU'] = list_code_cultu
    orientations['ID_PARCEL'] = list_ID_PARCEL
    orientations['NB_LINES'] = nb_lines_used
    orientations['WARNING'] = [
        f"multiple orientations ({n})" if n > 1 else "None" for n in nb_orientations]
    orientations['MEAN_LINES'] = [f"{num:.3f}" for num in mean_len_lines]
    orientations['STD_X_COORD'] = [f"{num:.3f}" for num in std_orientation_x]
    orientations['STD_Y_COORD'] = [f"{num:.3f}" for num in std_orientation_y]
    orientations['SLOPE'] = [f"{num:.3f}" for num in mean_slope_list]
    orientations['ASPECT'] = [f"{num:.3f}" for num in mean_aspect_list]
    orientations['CALC_ASPECT'] = [f"{num:.3f}" for num in calc_aspect]
    orientations['INDIC_ORIENTATION'] = [f"{num:.3f}" for num in indic_orient]
    orientations.crs = rpg.crs

    # Export and save the segments kept to compute the orientations
    if save_lsd:
        df = pd.DataFrame({'geometry': kept_lines})
        kept_lines = gpd.GeoDataFrame(df, columns=['geometry'])
        kept_lines['ID_PARCEL'] = ID_PARCEL_kept_lines
        kept_lines.crs = rpg.crs

        end_orientation = time.process_time() - start
        time_orientation_worker.set(
            time_orientation_worker.value + end_orientation)
        print(f"done ({len(orientations)} orientation(s) found)")
        return orientations, centroids, kept_lines
    else:
        end_orientation = time.process_time() - start
        time_orientation_worker.set(
            time_orientation_worker.value + end_orientation)
        print(f"done ({len(orientations)} orientation(s) found)")
        return orientations, centroids


def get_on_patch_border_lines(
    inputs,
    lsd_params,
    normalize,
    area_min,
    time_lsd,
    time_inter_mask_open,
    verbose
):
    """
        Detect the segment in the parcels located on the borders of the image patches

        Parameters
        ----------
        inputs: tuple containing the image path, the rpg parcels within the window and the rasterio.windows.Window to use to read the input image
        lsd_params: parameters for the LSD algorithm
        normalize: boolean indicating weither or not to normalize the input image

    """
    img_path, rpg, window = inputs

    start = time.process_time()

    rpg_expanded = rpg.buffer(1)
    with rasterio.open(img_path) as dataset:
        print(f"Patch {os.path.basename(img_path)} (borders)...", end="")
        profile = dataset.profile

        # Get new window
        src_transform = dataset.transform
        win_transform = rasterio.windows.transform(window, src_transform)
        window_bb = box(*rasterio.windows.bounds(window, src_transform))

        rpg_expanded = rpg.buffer(1).intersection(window_bb)

        profile = dataset.profile
        mask_dataset = dataset.read_masks(1, window=window)
        crs = dataset.crs

        img = dataset.read(window=window)

    if normalize:
        img = normalize_img(img, mask_dataset)

    # Mask with RPG and dataset mask
    mask_rpg = rasterio.features.rasterize(list(rpg_expanded),
                                           out_shape=img.shape[1:],
                                           transform=win_transform,
                                           fill=0,
                                           all_touched=True,
                                           dtype=rasterio.uint8)
    img = np.uint8(img)
    img = np.where(mask_dataset*mask_rpg, img, 0)

    if window is not None:
        profile.data["width"] = window.width
        profile.data["height"] = window.height
        profile.data["transform"] = win_transform
        profile.data["dtype"] = "uint8"

    # image monobande en entree de pyLSD
    img = np.mean(img[0:3], axis=0)

    time_inter_mask_open.set(
        time_inter_mask_open.value + time.process_time() - start)

    start_time_lsd = time.process_time()
    segments = lsd(
        np.asarray(img),
        scale=lsd_params["scale"],
        sigma_scale=lsd_params["sigma_scale"],
        quant=lsd_params["quant"],
        ang_th=lsd_params["ang_th"],
        eps=lsd_params["eps"],
        density_th=lsd_params["density_th"],
        n_bins=lsd_params["n_bins"])

    segments = list(map(partial(
        create_linestring,
        transform=profile["transform"],
        width_reduction=lsd_params["width_reduction"]),
        segments
    ))

    LSD = gpd.GeoDataFrame(segments, crs=crs)
    LSD.crs = rpg.crs

    lsd_dur = time.process_time() - start_time_lsd
    time_lsd.set(time_lsd.value + lsd_dur)

    gdf = []
    for ind in list(rpg.index):

        pol = rpg.at[ind, "geometry"]
        ID_PARCEL = rpg.at[ind, "ID_PARCEL"]

        # Erode the polygon edges to filter out the segments on the border
        erosion = - 5 * np.max([1, np.log((pol.area / area_min)**2)])
        within = LSD.within(pol.buffer(erosion))
        inter = LSD.loc[within]

        # The orientation calculation is applied only if the number of detected lines is over the threshold
        if inter.shape[0] < 1:
            if verbose:
                print(
                    f"Skipping parcel {ID_PARCEL}: no segment to compute the parcel orientation")
            continue

        vectx, vecty, len_lines, kept_lines = filter_segments(
            inter, lsd_params["min_len_line"])

        df = pd.DataFrame({'geometry': kept_lines})
        kept_lines = gpd.GeoDataFrame(df, columns=['geometry'])
        kept_lines['ID_PARCEL'] = [ID_PARCEL] * len(kept_lines)
        kept_lines["vectx"] = vectx
        kept_lines["vecty"] = vecty
        kept_lines["len_lines"] = len_lines
        kept_lines.crs = rpg.crs

        gdf.append(kept_lines)

    if gdf:
        gdf = gpd.GeoDataFrame(pd.concat(gdf), crs=crs)
        gdf.crs = rpg.crs
        print(f"done: {len(gdf)} parcels")

        return gdf

    return gpd.GeoDataFrame(gdf)


def get_on_patch_border_orientation(
    inputs,
    min_nb_line_per_parcelle,
    area_min,
    slope,
    aspect,
    time_slope_aspect,
    time_calculate_orientation,
    verbose
):
    delta_calculate_orientation = time.process_time()

    kept_lines, rpg = inputs

    pol = rpg.geometry.iloc[0]
    centroid = [pol.centroid]
    ID_PARCEL = rpg["ID_PARCEL"].iloc[0]
    code_cultu = rpg["CODE_CULTU"].iloc[0]
    code_group = rpg["CODE_GROUP"].iloc[0]

    vectx = kept_lines["vectx"].to_list()
    vecty = kept_lines["vecty"].to_list()
    len_lines = kept_lines["len_lines"].to_list()
    kept_lines = kept_lines.geometry.to_list()

    if len(vectx) <= (min_nb_line_per_parcelle * np.max([1, pol.area / area_min])):
        if verbose:
            print(
                f"Skipping parcel {ID_PARCEL}: not enough segments kept to compute the parcel orientation")
        return

    value_mean_slope, value_mean_aspect = get_mean_slope_aspect(
        pol, slope, aspect, time_slope_aspect)

    if value_mean_aspect is None or value_mean_slope is None:
        if verbose:
            print(
                f"Skipping parcel {ID_PARCEL}: mean slope value={value_mean_slope}, mean aspect value={value_mean_aspect}")
        return

    # Compute orientation
    orientation, value_calc_aspect, indic_orient = orientation_from_lines(
        vectx,
        vecty,
        pol,
        value_mean_aspect
    )

    # computes statistics for quality criteria
    mean_len_lines = [statistics.mean(len_lines)]
    nb_lines_used = [len(vectx)]
    std_orient_x = [statistics.stdev(vectx)]
    std_orient_y = [statistics.stdev(vecty)]

    nb_orientations, orient_dict = detect_multiple_orientations(
        kept_lines, vectx, vecty, len_lines, orientation, min_nb_line_per_parcelle)

    if orient_dict is not None:
        orientation = orient_dict["orientations"]
        centroid = orient_dict["centroids"]
        mean_len_lines = orient_dict["mean_len_lines"]
        nb_lines_used = orient_dict["nb_lines_used"]
        std_orient_x = orient_dict["std_orient_x"]
        std_orient_y = orient_dict["std_orient_y"]
    else:
        orientation = [orientation]

    delta_calculate_orientation = time.process_time() - delta_calculate_orientation
    time_calculate_orientation.set(
        time_calculate_orientation.value + delta_calculate_orientation)
    return orientation, centroid, code_group, code_cultu, nb_lines_used, nb_orientations, mean_len_lines, std_orient_x, std_orient_y, value_mean_slope, value_mean_aspect, value_calc_aspect, indic_orient, ID_PARCEL, kept_lines


def handle_on_patch_border_crops(
    rpg,
    list_on_border,
    lsd_params,
    area_min,
    slope,
    aspect,
    save_lsd,
    normalize,
    time_orientation_worker,
    time_calculate_orientation,
    time_lsd,
    time_inter_mask_open,
    time_slope_aspect,
    nb_cores,
    verbose
):

    start = time.process_time()

    with concurrent.futures.ProcessPoolExecutor(max_workers=nb_cores) as executor:
        kept_lines = list(executor.map(
            partial(get_on_patch_border_lines,
                    lsd_params=lsd_params,
                    normalize=normalize,
                    area_min=area_min,
                    time_lsd=time_lsd,
                    time_inter_mask_open=time_inter_mask_open,
                    verbose=verbose),
            list_on_border,
            chunksize=max([1, len(list_on_border) // nb_cores])
        ))
        kept_lines = gpd.geodataframe.GeoDataFrame(pd.concat(kept_lines))
        kept_lines.crs = rpg.crs
        # gather the filtered segments with the same ID_PARCEL using pd.unique
        kept_lines = [(kept_lines.loc[kept_lines["ID_PARCEL"] == id_parcel], rpg.loc[rpg["ID_PARCEL"] == id_parcel])
                      for id_parcel in pd.unique(kept_lines["ID_PARCEL"])]

        res = list(executor.map(
            partial(get_on_patch_border_orientation,
                    min_nb_line_per_parcelle=lsd_params["min_nb_line_per_parcelle"],
                    area_min=area_min,
                    slope=slope,
                    aspect=aspect,
                    time_slope_aspect=time_slope_aspect,
                    time_calculate_orientation=time_calculate_orientation,
                    verbose=verbose),
            kept_lines,
            chunksize=max([1, len(kept_lines) // nb_cores])
        ))

    orientations = []
    centroids = []
    list_code_group = []
    list_code_cultu = []
    nb_lines_used = []
    nb_orientations = []
    mean_len_lines = []
    std_orientation_x = []
    std_orientation_y = []
    mean_slope_list = []
    mean_aspect_list = []
    calc_aspect = []
    indic_orient = []
    list_ID_PARCEL = []
    kept_lines = []
    ID_PARCEL_kept_lines = []
    for r in res:
        if r is not None:
            orientations += r[0]
            centroids += r[1]
            list_code_group += [r[2]] * len(r[0])
            list_code_cultu += [r[3]] * len(r[0])
            nb_lines_used += r[4]
            nb_orientations += [r[5]] * len(r[0])
            mean_len_lines += r[6]
            std_orientation_x += r[7]
            std_orientation_y += r[8]
            mean_slope_list += [r[9]] * len(r[0])
            mean_aspect_list += [r[10]] * len(r[0])
            calc_aspect += [r[11]] * len(r[0])
            indic_orient += [r[12]] * len(r[0])
            list_ID_PARCEL += [r[13]] * len(r[0])
            kept_lines += r[14]
            ID_PARCEL_kept_lines += [r[13]] * len(r[14])

    conc_centroids = gpd.GeoDataFrame({"geometry": centroids})
    conc_centroids['CODE_GROUP'] = list_code_group
    conc_centroids['CODE_CULTU'] = list_code_cultu
    conc_centroids.crs = rpg.crs

    # export and save the final linestring orientations :
    conc_l = MultiLineString(orientations)
    orientations = gpd.GeoDataFrame(conc_l, columns=['geometry'])
    orientations['CODE_GROUP'] = list_code_group
    orientations['CODE_CULTU'] = list_code_cultu
    orientations['ID_PARCEL'] = list_ID_PARCEL
    orientations['NB_LINES'] = nb_lines_used
    orientations['WARNING'] = [
        f"multiple orientation ({n})" if n > 1 else "None" for n in nb_orientations]
    orientations['MEAN_LINES'] = [f"{num:.3f}" for num in mean_len_lines]
    orientations['STD_X_COORD'] = [f"{num:.3f}" for num in std_orientation_x]
    orientations['STD_Y_COORD'] = [f"{num:.3f}" for num in std_orientation_y]
    orientations['SLOPE'] = [f"{num:.3f}" for num in mean_slope_list]
    orientations['ASPECT'] = [f"{num:.3f}" for num in mean_aspect_list]
    orientations['CALC_ASPECT'] = [f"{num:.3f}" for num in calc_aspect]
    orientations['INDIC_ORIENTATION'] = [f"{num:.3f}" for num in indic_orient]
    orientations.crs = rpg.crs

    if save_lsd:
        df = pd.DataFrame({'geometry': kept_lines})
        kept_lines = gpd.GeoDataFrame(df, columns=['geometry'])
        kept_lines['ID_PARCEL'] = ID_PARCEL_kept_lines
        kept_lines.crs = rpg.crs

        end_orientation = time.process_time() - start
        time_orientation_worker.set(
            time_orientation_worker.value + end_orientation)
        print(f"done ({len(orientations)} orientation(s) found)")
    else:
        kept_lines = None
        end_orientation = time.process_time() - start
        time_orientation_worker.set(
            time_orientation_worker.value + end_orientation)
        print(f"done ({len(orientations)} orientation(s) found)")

    return orientations, conc_centroids, kept_lines


def get_rpg_patches(
    img_dataset,
    RPG,
    time_split,
    nb_cores,
    patch_size=None,
    mode=""
):
    """
        Construct the lists used for parallelization with multiprocessing.
        If the input image dataset is one image path:
            We construct a list of Tuples containing the image path, RPG within Window, and Window
            by doing the parallelization on the list of windows
        If the input image dataset is a list of images path:
            We construct a list of Tuples containing the image path, RPG within Window, and Window
            by doing the parallelization on the list of images.

        Parameters
        ----------
        img_dataset: list or str containing the image(s) path

        RPG: the input RPG
        time_split: variable shared between processes to track process time
        windows: the list of rasterio.windows.Window
        mode: str to choose to construct the list for the image(s) borders or not

        Returns
        -------
        list_rpg_patches: the list of Tuples containing image path, RPG within the window and fully within the image extent, and the Window
        list_on_border: the list of Tuples containing image path, RPG within the window and on the image border, and the Window



    """

    print("Splitting the RPG into patches...", end="")

    with Manager() as manager:
        list_rpg_patches = manager.list()
        list_on_border = manager.list()
        with concurrent.futures.ProcessPoolExecutor(max_workers=nb_cores) as executor:
            if isinstance(img_dataset, list):
                if mode == "border":
                    res = list(executor.map(partial(split_img_borders,
                                                    RPG=RPG,
                                                    patch_size=patch_size,
                                                    list_on_border=list_on_border,
                                                    time_split=time_split),
                                            img_dataset,
                                            chunksize=max(
                                                [1, len(img_dataset) // nb_cores])
                                            ))
                    print("done: {:.3} seconds".format(time_split.value))
                    return list(list_on_border)
                else:
                    res = list(executor.map(partial(split_img_dataset,
                                                    RPG=RPG,
                                                    patch_size=patch_size,
                                                    list_rpg_patches=list_rpg_patches,
                                                    time_split=time_split),
                                            img_dataset,
                                            chunksize=max(
                                                [1, len(img_dataset) // nb_cores])
                                            ))
                    print("done: {:.3} seconds".format(time_split.value))
                    return list(list_rpg_patches)
            else:
                if mode != "border":
                    if patch_size:
                        with rasterio.open(img_dataset) as dataset:
                            num_rows, num_cols = dataset.shape

                        windows = [rasterio.windows.Window(i, j, min(num_rows-i, patch_size), min(num_cols-j, patch_size))
                                for i in range(0, num_rows, patch_size) for j in range(0, num_cols, patch_size)]

                        res = list(executor.map(partial(split_windows,
                                                        img_path=img_dataset,
                                                        RPG=RPG,
                                                        list_rpg_patches=list_rpg_patches,
                                                        time_split=time_split),
                                                windows,
                                                chunksize=max([1, len(windows) // nb_cores])
                                                ))
                    else:
                        split_windows(window=None,
                                    img_path=img_dataset,
                                    RPG=RPG,
                                    list_rpg_patches=list_rpg_patches,
                                    time_split=time_split
                                    )

                print("done: {:.3} seconds".format(time_split.value))
                return list(list_rpg_patches)


def main(args):

    # Log params
    args_dict = vars(args)
    for key in args_dict:
        print(f"{key}: {args_dict[key]}")

    print(f"Commit hash: {get_commit_hash()}")
    start_main = time.process_time()
    start = datetime.now()

    # Open rpg shapefile
    print("Reading RPG shapefile...", end="")
    RPG = gpd.read_file(args.rpg)
    print("done: {:.3} seconds".format(time.process_time() - start_main))
    crs_rpg = RPG.crs
    crs = {"init": "epsg:2154"}

    inter_railroad = None
    if args.railroad_file:
        df_railroad = gpd.read_file(args.railroad_file)
        df_railroad_buff = gpd.GeoDataFrame(
            {"geometry": df_railroad.to_crs(crs).buffer(args.distance_to_the_way_max).to_list()})
        inter_railroad = gpd.overlay(RPG.to_crs(crs), df_railroad_buff, how="intersection")
        inter_railroad = inter_railroad["ID_PARCEL"].to_list()

    img_dataset = sorted(glob.glob(args.img + "/*." + args.type)
                         ) if os.path.isdir(args.img) else args.img

    with rasterio.open(img_dataset[0] if isinstance(img_dataset, list) else img_dataset) as dataset:
        num_rows, num_cols = dataset.shape

    del os.environ['PROJ_LIB']

    lsd_params = {
        "min_nb_line_per_parcelle": args.min_nb_line_per_parcelle,
        "min_len_line": args.min_len_line,
        "scale": args.scale,
        "width_reduction": args.width_reduction,
        "sigma_scale": args.sigma_scale,
        "quant": args.quant,
        "ang_th": args.ang_th,
        "eps": args.eps,
        "density_th": args.density_th,
        "n_bins": args.n_bins
    }

    manager = Manager()
    time_split = manager.Value("time_split", 0.)
    time_slope_aspect = manager.Value("time_slope_aspect", 0.)
    time_lsd = manager.Value("time_lsd", 0.)
    time_orientation_worker = manager.Value("time_orientation_worker", 0.)
    time_calculate_orientation = manager.Value(
        "time_calculate_orientation", 0.)
    time_inter_mask_open = manager.Value("time_inter_mask_open", 0.)
    parcel_ids_processed = manager.list()

    len_RPG = len(RPG)

    # Split RPG into patches
    list_rpg_patches = get_rpg_patches(
        img_dataset,
        RPG,
        time_split,
        args.nb_cores,
        patch_size=args.patch_size
    )

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.nb_cores) as executor:

        list_gdf = list(executor.map(
            partial(orientation_worker,
                    normalize=args.normalize,
                    parcel_ids_processed=parcel_ids_processed,
                    lsd_params=lsd_params,
                    slope=args.slope,
                    aspect=args.aspect,
                    area_min=args.area_min,
                    time_inter_mask_open=time_inter_mask_open,
                    time_slope_aspect=time_slope_aspect,
                    time_lsd=time_lsd,
                    time_orientation_worker=time_orientation_worker,
                    time_calculate_orientation=time_calculate_orientation,
                    save_lsd=args.save_lsd,
                    verbose=args.verbose),
            list_rpg_patches,
            chunksize=max([1, len(img_dataset) // args.nb_cores])
        ))

    del list_rpg_patches

    start_concat = time.process_time()
    orientations = gpd.geodataframe.GeoDataFrame(
        pd.concat([r[0] for r in list_gdf]), crs=crs)
    orientations.crs = crs
    orientations.to_file(args.out_shp.split(".")[0] + "_orientations.shp")
    print("len orientations:", len(orientations))
    del orientations

    centroids = gpd.geodataframe.GeoDataFrame(
        pd.concat([r[1] for r in list_gdf]), crs=crs)
    centroids.crs = crs
    centroids.to_file(args.out_shp.split(".")[0] + "_centroids.shp")
    print("len centroids:", len(centroids))
    del centroids

    if args.save_lsd:
        kept_lines = gpd.geodataframe.GeoDataFrame(
            pd.concat([r[2] for r in list_gdf]), crs=crs)
        kept_lines.crs = crs
        kept_lines.to_file(args.out_shp.split(".")[0] + "_kept_lines.shp")
        print("len kept_lines:", len(kept_lines))

        del kept_lines

    print("Time to concatenate results: {:.3}s".format(
        time.process_time() - start_concat))

    del list_gdf

    list_on_border = get_rpg_patches(
        img_dataset,
        RPG,
        time_split,
        args.nb_cores,
        patch_size=args.patch_size,
        mode="border"
    )

    on_border_orient = gpd.geodataframe.GeoDataFrame([])
    on_border_centroids = gpd.geodataframe.GeoDataFrame([])
    on_border_lines = gpd.geodataframe.GeoDataFrame([])
    if list_on_border:
        on_border_orient, on_border_centroids, on_border_lines = handle_on_patch_border_crops(
            RPG,
            list_on_border,
            lsd_params,
            args.area_min,
            args.slope,
            args.aspect,
            args.save_lsd,
            args.normalize,
            time_orientation_worker,
            time_calculate_orientation,
            time_lsd,
            time_inter_mask_open,
            time_slope_aspect,
            args.nb_cores,
            args.verbose
        )

    crs_rpg = RPG.crs

    del list_on_border
    del RPG

    def sec_to_hms(dt):
        h = int(dt // 3600)
        m = int((dt - h*3600) // 60)
        s = dt - h*3600 - m*60

        h = "0"+str(h) if h < 10 else h
        m = "0"+str(m) if m < 10 else m
        s = "0"+str(s) if s < 10 else s
        return "{}:{}:{:.3}".format(h, m, s)

    start_concat = time.process_time()
    orientations = gpd.read_file(args.out_shp.split(".")[
                                 0] + "_orientations.shp")
    orientations = gpd.geodataframe.GeoDataFrame(
        pd.concat([orientations, on_border_orient]), crs=crs)

    orientations.crs = crs
    if inter_railroad is not None:
        mask_inter = orientations["ID_PARCEL"].isin(inter_railroad)

        inter_orientations = orientations.loc[mask_inter].to_crs({"init": "epsg:4326"})

        df_railroad.crs = {'init' :'epsg:4326'}
        df_railroad.to_crs({"init": "epsg:4326"}, inplace=True)
        angles = azimuth_angles_with_railroad(inter_orientations, df_railroad)

        orient_a = orientations.loc[mask_inter].reset_index(drop=True)
        orient_a["azimuth_railroad"] = angles
        orient_b = orientations.loc[~mask_inter].reset_index(drop=True)
        orient_b["azimuth_railroad"] = ["None" for _ in range(len(orient_b))]

        orientations = gpd.geodataframe.GeoDataFrame(
            pd.concat([orient_a, orient_b], ignore_index=True), crs=crs)

    orientations.to_crs(crs, inplace=True)
    orientations.to_file(args.out_shp.split(".")[0] + "_orientations.shp")
    len_orientation = len(orientations)
    print("len orientations:", len_orientation)
    del orientations

    centroids = gpd.read_file(args.out_shp.split(".")[0] + "_centroids.shp")
    centroids = gpd.geodataframe.GeoDataFrame(
        pd.concat([centroids, on_border_centroids]), crs=crs)
    centroids.to_crs(crs, inplace=True)
    centroids.to_file(args.out_shp.split(".")[0] + "_centroids.shp")
    print("len centroids:", len(centroids))
    del centroids

    if args.save_lsd:
        kept_lines = gpd.read_file(args.out_shp.split(".")[0] + "_kept_lines.shp")
        kept_lines = gpd.geodataframe.GeoDataFrame(
            pd.concat([kept_lines, on_border_lines]), crs=crs)
        kept_lines.to_crs(crs, inplace=True)
        kept_lines.to_file(args.out_shp.split(".")[0] + "_kept_lines.shp")
        print("len kept_lines:", len(kept_lines))
        del kept_lines

    print("Time to concatenate results: {:.3}s".format(
        time.process_time() - start_concat))

    time_main = time.process_time() - start_main

    data = list(map(sec_to_hms,
                    [time_main+time_orientation_worker.value,
                     time_main,
                     time_orientation_worker.value,
                     time_slope_aspect.value,
                     time_lsd.value,
                     time_inter_mask_open.value,
                     time_calculate_orientation.value]
                    )
                )
    data_norm = list(map(sec_to_hms,
                         [time_main+time_orientation_worker.value / args.nb_cores,
                          time_main,
                          time_orientation_worker.value / args.nb_cores,
                          time_slope_aspect.value / args.nb_cores,
                          time_lsd.value / args.nb_cores,
                          time_inter_mask_open.value / args.nb_cores]
                         )
                     )
    data += [len_orientation, len_RPG,
             f"{int(100*len_orientation/len_RPG)}%"]
    header = ["all", "main", "worker", "slope_aspect", "lsd", "img_processing",
              "calculate_orientation", "num_orientations", "RPG_length", "ratio"]

    # Save time logs to csv
    with open(args.out_csv, "w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(header)
        csv_writer.writerow(data)

    format_line = "{:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {}"
    print("PROCESS TIME:")
    print(format_line.format("", *header[:-4]))
    print(format_line.format("All processes", *data[:-4]))
    print(format_line.format("Per process", *data_norm))

    print(
        f"\nAverage time for 1 image of size={num_rows,num_cols}: {sec_to_hms(time_orientation_worker.value / len(img_dataset))}")
    print(
        f"Average time for LSD on 1 crop: {sec_to_hms(time_lsd.value / len_orientation)}")

    end = datetime.now() - start
    print(f"\nDatetime: {end}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Detection of crop orientation on BDORTHO and PHR images')
    parser.add_argument(
        '-img', '--img', metavar='[IMAGE]', help='Image path or directory containing the images', required=True)
    parser.add_argument(
        '-rpg', '--rpg', metavar='[RPG]', help='Input RPG shapefile', required=True)
    parser.add_argument(
        '-railroad_file', '--railroad_file', help='Input railroad network shapefile', required=True)
    parser.add_argument('-out_shp', '--out_shp',
                        default=None, help='Output shapefile')
    parser.add_argument('-out_csv', '--out_csv',
                        default=None, help='Output csv file')
    parser.add_argument('-slope', '--slope', required=True)
    parser.add_argument('-aspect', '--aspect', required=True)
    parser.add_argument('-nb_cores', '--nb_cores', type=int, default=5)
    parser.add_argument(
        '-type', '--type', metavar='[TYPE]', help='file extension for the image(s)', default="tif")
    parser.add_argument('-normalize', '--normalize', action="store_true")
    parser.add_argument('-save_lsd', '--save_lsd', action="store_true")
    parser.add_argument('-verbose', '--verbose', action="store_true")
    parser.add_argument('-patch_size', '--patch_size', type=int, default=10000)
    parser.add_argument('-area_min', '--area_min', type=float, default=20000.)
    parser.add_argument('-distance_to_the_way_max', '--distance_to_the_way_max', type=float, default=2000.)

    group = parser.add_argument_group(title="LSD params")
    group.add_argument(
        '-min_nline', '--min_nb_line_per_parcelle', type=int, default=20)
    group.add_argument('-min_len_line', '--min_len_line', type=int, default=8)
    group.add_argument('-scale', '--scale', type=float, default=0.8)
    group.add_argument('-wr', '--width_reduction', type=float, default=1.0)
    group.add_argument('-sigma_scale', '--sigma_scale',
                       type=float, default=0.6)
    group.add_argument('-quant', '--quant', type=float, default=2.0)
    group.add_argument('-ang_th', '--ang_th', type=float, default=26.0)
    group.add_argument('-eps', '--eps', type=float, default=0.0)
    group.add_argument('-density_th', '--density_th', type=float, default=0.7)
    group.add_argument('-n_bins', '--n_bins', type=int, default=255)

    parser.print_help()
    args = parser.parse_args()

    main(args)
