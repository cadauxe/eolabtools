# import geopandas as gpd
import rasterio
import numpy as np
import os
import filecmp
# import fiona

import pandas as pd


def compare_csv(file1, file2):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Sort both DataFrames by all columns
    df1_sorted = df1.sort_values(by=list(df1.columns)).reset_index(drop=True)
    df2_sorted = df2.sort_values(by=list(df2.columns)).reset_index(drop=True)

    if not df1_sorted.equals(df2_sorted):
        raise ValueError(f"CSV files differ: {file1} and {file2}")


def compare_shapefiles(file1, file2):
    """
    Compare two shapefiles.

    Raises:
        ValueError: If shapefiles are different
    """
    if not filecmp.cmp(file1, file2, shallow=False):
        raise ValueError(f"Error comparing {file1} and {file2}")



def equal_lines_content(gdf_ref, gdf_test, ref_cols) -> bool:
    """
    """
    for idx in range(len(gdf_ref)):
        for col in ref_cols:
            ref_val = gdf_ref.iloc[idx][col]
            test_val = gdf_test.iloc[idx][col]

            if col == 'geometry':
                # Compare geometries
                if ref_val is None and test_val is None:
                    pass
                elif (ref_val is None) != (test_val is None) or not ref_val.equals(test_val):
                    return False
            else:
                # Compare attributes
                if not (pd.isna(ref_val) and pd.isna(test_val)) and str(ref_val) != str(test_val):
                    print(f"  Row {idx}: Attribute '{col}' mismatch")
                    print(f"    File1: {ref_val}")
                    print(f"    File2: {test_val}")
                    return False
    return True


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

    print("TIFF files are identical.")
    return True


# def compare_gpkg(file1, file2):
#     layers1 = fiona.listlayers(file1)
#     layers2 = fiona.listlayers(file2)
#
#     common_layers = set(layers1).intersection(layers2)
#
#     for layer in common_layers:
#         gdf1 = gpd.read_file(file1, layer=layer)
#         gdf2 = gpd.read_file(file2, layer=layer)
#
#         # Columns to compare
#         ref_cols = [col for col in gdf1.columns]
#         test_cols = [col for col in gdf2.columns]
#
#         if set(ref_cols) != set(test_cols):
#           raise ValueError(f"Error comparing {file1} and {file2}")
#
#         if not(equal_lines_content(gdf1, gdf2, test_cols)) :
#           raise ValueError(f"Error comparing {file1} and {file2}")


def compare_files(reference_dir : str, output_dir : str, tool : str):
    """
    TO DO
    """
    ref_files = sorted(os.listdir(reference_dir))
    out_test_files = sorted(os.listdir(output_dir))

    if ref_files == out_test_files:
        print("Both directories contain the same filenames.")
    else:
        raise Exception("Filenames differ between the directories.\n"
                            f"Only in {reference_dir} : {[item for item in ref_files if item not in out_test_files]}\n"
                            f"Only in {output_dir} : {[item for item in out_test_files if item not in ref_files]}")

    # Compare output files with references
    if tool == "NightOSM":
        pass
    elif tool == "SunMapGen":
        for f in ref_files :
            if ".tif" in f:
                # Compare tif files (pixel value and metadata)
                compare_tif(f"{output_dir}/{f}", f"{reference_dir}/{f}")
            # elif ".gpkg" in f:
                # Compare gpkg files
                # compare_gpkg(f"{output_dir}/{f}", f"{reference_dir}/{f}")
    elif tool == "DetecOrCult":
        for f in ref_files:
            if f == "computation_time.csv" :
                continue
            if any(ext in f for ext in [".shp"]):
                # Compare shapefiles
                compare_shapefiles(f"{output_dir}/{f}", f"{reference_dir}/{f}")
            elif ".csv" in f :
                # Compare csv files
                compare_csv(f"{output_dir}/{f}", f"{reference_dir}/{f}")
        print("Both directories contain the same files.")
