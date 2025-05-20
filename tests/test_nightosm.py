from conftest import EOLabtoolsTestsPath
import subprocess
from test_utils import compare_files
import pytest
import os
from pathlib import Path
import subprocess
import sys

@pytest.mark.ci
def test_nightosm_rasterize_radiance(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """

    ###Modifier dynamiquement les fichiers de configs

    command = [
        f"night_osm_image_registration",
        f"-o", f"{eolabtools_paths.nightosm_outdir}/test_nightosm_rasterize_radiance/",
        f"--config", f"{eolabtools_paths.nightosm_datadir}/config/config1.yml",
        f"--osm-config", f"{eolabtools_paths.nightosm_datadir}/osm-config/osm_config_subtracted.yml",
        f"{eolabtools_paths.nightosm_datadir}/Extrait1/Extract1-Radiance.tif"
    ]
    print(command)

    result = subprocess.run(command, capture_output=True, text=True, check=True)

    # compare_files(reference_dir = f"{eolabtools_paths.sunmap_ref}/test_1tile_low_res",
    #               output_dir = f"{eolabtools_paths.sunmap_outdir}/test_1tile_low_res_lst",
    #               tool = "SunMapGen")


@pytest.mark.ci
def test_nightosm_rasterize_rgb(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    command = [
        f"python",
        f"src/eolabtools/sun_map_generation/SunMapGenerator.py",
        f"--digital_surface_model", f"{eolabtools_paths.sunmap_datadir}/test_1tile_low_res/75-2021-0659-6861-LA93-0M50.tif",
        f"--tiles_file", f"{eolabtools_paths.sunmap_datadir}/test_1tile_low_res/1tile.shp",
        f"--area", f"Paris",
        f"--date", f"2024-08-03", f"2024-08-04", f"1",
        f"--time", f"08:00", f"17:00", f"120",
        f"--nb_cores", f"32",
        f"--occ_changes", f"3",
        f"--output_dir", f"{eolabtools_paths.sunmap_outdir}/test_1tile_low_res_tif/"
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stderr)

    compare_files(reference_dir = f"{eolabtools_paths.sunmap_ref}/test_1tile_low_res",
                  output_dir = f"{eolabtools_paths.sunmap_outdir}/test_1tile_low_res_tif",
                  tool = "SunMapGen")


@pytest.mark.ci
def test_nightosm_register_radiance(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    command = [
        f"python",
        f"src/eolabtools/sun_map_generation/SunMapGenerator.py",
        f"--digital_surface_model", f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/listing_2tiles.lst",
        f"--tiles_file", f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/2tiles.shp",
        f"--area", f"Paris",
        f"--date", f"2024-08-31", f"2024-08-31", f"1",
        f"--time", f"08:00", f"9:00", f"60",
        f"--nb_cores", f"32",
        f"--occ_changes", f"3",
        f"--output_dir", f"{eolabtools_paths.sunmap_outdir}/test_2tiles_low_res/",
        f"--save_temp"
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stderr)

    os.remove(f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/listing_2tiles.lst")

    compare_files(reference_dir = f"{eolabtools_paths.sunmap_ref}/test_2tiles_low_res",
                  output_dir = f"{eolabtools_paths.sunmap_outdir}/test_2tiles_low_res",
                  tool = "SunMapGen")


@pytest.mark.ci
def test_nightosm_register_rgb(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    command = [
        f"python",
        f"src/eolabtools/sun_map_generation/SunMapGenerator.py",
        f"--digital_surface_model", f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/listing_2tiles.lst",
        f"--tiles_file", f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/2tiles.shp",
        f"--area", f"Paris",
        f"--date", f"2024-08-31", f"2024-08-31", f"1",
        f"--time", f"08:00", f"9:00", f"60",
        f"--nb_cores", f"32",
        f"--occ_changes", f"3",
        f"--output_dir", f"{eolabtools_paths.sunmap_outdir}/test_2tiles_low_res/",
        f"--save_temp"
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stderr)

    os.remove(f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/listing_2tiles.lst")

    compare_files(reference_dir = f"{eolabtools_paths.sunmap_ref}/test_2tiles_low_res",
                  output_dir = f"{eolabtools_paths.sunmap_outdir}/test_2tiles_low_res",
                  tool = "SunMapGen")


@pytest.mark.ci
def test_nightosm_simple_config(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    command = [
        f"python",
        f"src/eolabtools/sun_map_generation/SunMapGenerator.py",
        f"--digital_surface_model", f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/listing_2tiles.lst",
        f"--tiles_file", f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/2tiles.shp",
        f"--area", f"Paris",
        f"--date", f"2024-08-31", f"2024-08-31", f"1",
        f"--time", f"08:00", f"9:00", f"60",
        f"--nb_cores", f"32",
        f"--occ_changes", f"3",
        f"--output_dir", f"{eolabtools_paths.sunmap_outdir}/test_2tiles_low_res/",
        f"--save_temp"
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stderr)

    os.remove(f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/listing_2tiles.lst")

    compare_files(reference_dir = f"{eolabtools_paths.sunmap_ref}/test_2tiles_low_res",
                  output_dir = f"{eolabtools_paths.sunmap_outdir}/test_2tiles_low_res",
                  tool = "SunMapGen")
