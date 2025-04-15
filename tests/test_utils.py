import rasterio
import numpy as np
import geopandas as gpd
import os


def compare_tif(file1, file2, atol=1e-10):
    with rasterio.open(file1) as src1, rasterio.open(file2) as src2:
        # Compare metadata
        if src1.meta != src2.meta:
            print("TIFF metadata differs.")
            return False

        # Compare pixel data
        arr1 = src1.read()
        arr2 = src2.read()
        if not np.allclose(arr1, arr2, atol=atol):
            print("TIFF pixel values differ.")
            return False

    print("TIFF files are identical.")
    return True


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
        print("GPKG files differ.")
        return False


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
    if tool == "SunMapGen":
        for f in ref_files :
            if ".tif" in f:
                # Compare tif files (pixel value and metadata)
                compare_tif(f"{out_test_files}/{f}", f"{ref_files}/{f}")
            elif ".gpkg" in f:
                # Compare gpkg files
                compare_gpkg(f"{out_test_files}/{f}", f"{ref_files}/{f}")

    elif tool == "NightOSM":
        pass
    elif tool == "DetecOrCult":
        pass


