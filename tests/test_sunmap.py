from tests.conftest import EOLabtoolsTestsPath
from tests.test_utils import compare_files, clear_outdir, create_outdir
from src.eolabtools.sun_map_generation.SunMapGenerator import sun_map_generation
import pytest
import os

@pytest.mark.ci
def test_sunmap_1tile_lst(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    with open(f"{eolabtools_paths.sunmap_datadir}/test_1tile_low_res/listing_1tile.lst", "w") as f:
        f.write(f"{eolabtools_paths.sunmap_datadir}/test_1tile_low_res/75-2021-0659-6861-LA93-0M50.tif" + "\n")

    create_outdir(f"{eolabtools_paths.sunmap_outdir}/test_1tile_low_res_lst/")

    sun_map_generation(
        digital_surface_model=f"{eolabtools_paths.sunmap_datadir}/test_1tile_low_res/listing_1tile.lst",
        tiles_file=f"{eolabtools_paths.sunmap_datadir}/test_1tile_low_res/1tile.shp",
        date=["2024-08-03", "2024-08-04", "1"],
        time=["08:00", "17:00", "120"],
        occ_changes=3,
        nb_cores=32,
        output_dir=f"{eolabtools_paths.sunmap_outdir}/test_1tile_low_res_lst/",
        save_temp=False,
        save_masks=False
    )

    compare_files(reference_dir = f"{eolabtools_paths.sunmap_ref}/test_1tile_low_res",
                  output_dir = f"{eolabtools_paths.sunmap_outdir}/test_1tile_low_res_lst",
                  tool = "SunMapGen")

    os.remove(f"{eolabtools_paths.sunmap_datadir}/test_1tile_low_res/listing_1tile.lst")
    clear_outdir(f"{eolabtools_paths.sunmap_outdir}/test_1tile_low_res_lst/")


@pytest.mark.ci
def test_sunmap_1tile_tif(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    create_outdir(f"{eolabtools_paths.sunmap_outdir}/test_1tile_low_res_tif/")

    sun_map_generation(
        digital_surface_model=f"{eolabtools_paths.sunmap_datadir}/test_1tile_low_res/75-2021-0659-6861-LA93-0M50.tif",
        tiles_file=f"{eolabtools_paths.sunmap_datadir}/test_1tile_low_res/1tile.shp",
        date=["2024-08-03", "2024-08-04", "1"],  # CLI → list
        time=["08:00", "17:00", "120"],  # CLI → list
        occ_changes=3,
        nb_cores=32,
        output_dir=f"{eolabtools_paths.sunmap_outdir}/test_1tile_low_res_tif/",
        save_temp=False,
        save_masks=False
    )

    compare_files(reference_dir = f"{eolabtools_paths.sunmap_ref}/test_1tile_low_res",
                  output_dir = f"{eolabtools_paths.sunmap_outdir}/test_1tile_low_res_tif",
                  tool = "SunMapGen")

    clear_outdir(f"{eolabtools_paths.sunmap_outdir}/test_1tile_low_res_tif/")


@pytest.mark.ci
def test_sunmap_2tiles(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    with open(f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/listing_2tiles.lst", "w") as f:
        f.write(f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/75-2021-0648-6862-LA93-0M50.tif"
                + "\n"
                + f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/75-2021-0649-6862-LA93-0M50.tif" )

    create_outdir(f"{eolabtools_paths.sunmap_outdir}/test_2tiles_low_res/")

    sun_map_generation(
        digital_surface_model=f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/listing_2tiles.lst",
        tiles_file=f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/2tiles.shp",
        date=["2024-08-31", "2024-08-31", "1"],
        time=["08:00", "9:00", "60"],
        occ_changes=3,
        nb_cores=32,
        output_dir=f"{eolabtools_paths.sunmap_outdir}/test_2tiles_low_res/",
        save_temp=True,
        save_masks=False
    )

    compare_files(reference_dir = f"{eolabtools_paths.sunmap_ref}/test_2tiles_low_res",
                  output_dir = f"{eolabtools_paths.sunmap_outdir}/test_2tiles_low_res",
                  tool = "SunMapGen")

    os.remove(f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/listing_2tiles.lst")
    clear_outdir(f"{eolabtools_paths.sunmap_outdir}/test_2tiles_low_res/")