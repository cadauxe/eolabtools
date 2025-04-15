import sys
for path in sys.path:
    print(path)

from conftest import EOLabtoolsTestsPath
import subprocess
from test_utils import compare_files
import pytest

@pytest.mark.ci
def test_sunmap_1tile(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    command = [
        f"python",
        f"src/eolabtools/sun_map_generation/SunMapGenerator.py",
        f"--digital_surface_model", f"{eolabtools_paths.sunmap_datadir}/test_1tile_low_res/listing_1tile.lst",
        f"--tiles_file", f"{eolabtools_paths.sunmap_datadir}/test_1tile_low_res/1tile.shp",
        f"--area", f"Paris",
        f"--date", f"2024-08-03", f"2024-08-04", f"1",
        f"--time", f"08:00", f"17:00", f"120",
        f"--nb_cores", f"32",
        f"--occ_changes", f"3",
        f"--output_dir", f"{eolabtools_paths.sunmap_outdir}/test_1tile_low_res/"
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stderr)

    compare_files(reference_dir = f"{eolabtools_paths.sunmap_ref}/test_1tile_low_res",
                  output_dir = f"{eolabtools_paths.sunmap_outdir}/test_1tile_low_res",
                  tool = "SunMapGen")


@pytest.mark.ci
def test_sunmap_2tile(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    command = [
        f"python",
        f"src/eolabtools/sun_map_generation/SunMapGenerator.py",
        f"--digital_surface_model", f"{eolabtools_paths.sunmap_datadir}/test_2tile_low_res/listing_2tiles.lst",
        f"--tiles_file", f"{eolabtools_paths.sunmap_datadir}/test_2tiles_low_res/2tiles.shp",
        f"--area", f"Paris",
        f"--date", f"2024-08-31", f"2024-08-31", f"1",
        f"--time", f"08:00", f"9:00", f"60",
        f"--nb_cores", f"32",
        f"--occ_changes", f"3",
        f"--output_dir", f"{eolabtools_paths.sunmap_outdir}/test_2tiles_low_res/"
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stderr)

    compare_files(reference_dir = f"{eolabtools_paths.sunmap_ref}/test_2tiles_low_res",
                  output_dir = f"{eolabtools_paths.sunmap_outdir}/test_2tiles_low_res",
                  tool = "SunMapGen")