import geopandas as gpd
import rasterio
import numpy as np
import os
from glob import glob

import filecmp
import pandas as pd

def get_all_files(reference_dir):
    all_files = glob(os.path.join(reference_dir, "**", "*"), recursive=True)
    # Filter only files (exclude directories)
    just_files = [f.split(reference_dir + '/')[-1] for f in all_files if os.path.isfile(f)]
    return just_files

def compare_csv(file1, file2):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Sort both DataFrames by all columns
    df1_sorted = df1.sort_values(by=list(df1.columns)).reset_index(drop=True)
    df2_sorted = df2.sort_values(by=list(df2.columns)).reset_index(drop=True)

    if not df1_sorted.equals(df2_sorted):
        raise ValueError(f"CSV files differ: {file1} and {file2}")


def compare_shapefiles(file1, file2):
    if not filecmp.cmp(file1, file2, shallow=False):
        raise ValueError(f"Error comparing {file1} and {file2}")


def compare_tif(file1, file2, atol=1e-10):
    with rasterio.open(file1) as src1, rasterio.open(file2) as src2:
        # Compare metadata
        if src1.meta != src2.meta:
            raise ValueError(f"TIFF metadata differs.")

        # Compare pixel data
        arr1 = src1.read()
        arr2 = src2.read()
        if not np.allclose(arr1, arr2, atol=atol):
            raise ValueError(f"TIFF pixel values differ.")


def compare_gpkg(file1, file2):
    gdf1 = gpd.read_file(file1)
    gdf2 = gpd.read_file(file2)

    # Sort to ensure consistent ordering
    gdf1 = gdf1.sort_values(by=gdf1.columns.tolist()).reset_index(drop=True)
    gdf2 = gdf2.sort_values(by=gdf2.columns.tolist()).reset_index(drop=True)

    if gdf1.equals(gdf2):
        print("GPKG files are identical.")
        return True
    else:
        raise ValueError(f"GPKG files differ.")


def compare_files(reference_dir : str, output_dir : str, tool : str):
    """
    TO DO
    """
    ref_files = get_all_files(reference_dir)
    out_test_files = get_all_files(output_dir)

    if ref_files == out_test_files:
        print("Both directories contain the same filenames.")
    else:
        raise Exception("Filenames differ between the directories.\n"
                            f"Only in {reference_dir} : {[item for item in ref_files if item not in out_test_files]}\n"
                            f"Only in {output_dir} : {[item for item in out_test_files if item not in ref_files]}")

    # Compare output files with references
    if tool == "NightOSM":
        print(ref_files)
        for f in ref_files :
            if ".tif" in f:
                # Compare tif files (pixel value and metadata)
                compare_tif(f"{output_dir}/{f}", f"{reference_dir}/{f}")
            elif ".csv" in f :
                # Compare csv files
                compare_csv(f"{output_dir}/{f}", f"{reference_dir}/{f}")
            elif ".gpkg" in f:
                # Compare gpkg files
                compare_gpkg(f"{output_dir}/{f}", f"{reference_dir}/{f}")
    elif tool == "SunMapGen":
        for f in ref_files :
            if ".tif" in f:
                # Compare tif files (pixel value and metadata)
                compare_tif(f"{output_dir}/{f}", f"{reference_dir}/{f}")
            elif ".gpkg" in f:
                # Compare gpkg files
                compare_gpkg(f"{output_dir}/{f}", f"{reference_dir}/{f}")
    elif tool == "DetecOrCult":
        for f in ref_files:
            if any(ext in f for ext in [".shp", ".dbf", ".prj", ".cpg", ".shx"]):
                # Compare shapefiles
                compare_shapefiles(f"{output_dir}/{f}", f"{reference_dir}/{f}")
            elif ".csv" in f :
                # Compare csv files
                compare_csv(f"{output_dir}/{f}", f"{reference_dir}/{f}")
        print("Both directories contain the same files.")


