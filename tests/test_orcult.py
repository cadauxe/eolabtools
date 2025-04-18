from conftest import EOLabtoolsTestsPath
import subprocess
from test_utils import compare_files
import pytest


def test_plot_orientation(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    command = [
        f"python",
        f"src/eolabtools/detection_orientation_culture/orientation_detection.py",
        f"--img", f"{eolabtools_paths.plotor_datadir}/LeHavre_2017_mosaic_crop.tif",
        f"--type", f"tif",
        f"--rpg", f"{eolabtools_paths.plotor_datadir}/RPG/RPG_LeHavre_2017.shp",
        f"--output_dir", f"{eolabtools_paths.plotor_outdir}/2017_final",
        f"--nb_cores", f"4",
        f"--patch_size", f"10000",
        f"--slope", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_SLOPE_crop.tif",
        f"--aspect", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_ASPECT_crop.tif",
        f"--save_fld",
        f"--verbose"
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stderr)

    compare_files(reference_dir = f"{eolabtools_paths.plotor_ref}/2017_final",
                  output_dir = f"{eolabtools_paths.plotor_outdir}/2017_final",
                  tool = "DetecOrCult")

@pytest.mark.ci
def test_plot_orientation_cut(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    command = [
        f"python",
        f"src/eolabtools/detection_orientation_culture/orientation_detection.py",
        f"--img", f"{eolabtools_paths.plotor_datadir}/LeHavre_2017_mosaic_crop_cut.tif",
        f"--type", f"tif",
        f"--rpg", f"{eolabtools_paths.plotor_datadir}/RPG/RPG_LeHavre_2017_cropped.shp",
        f"--output_dir", f"{eolabtools_paths.plotor_outdir}/2017_final_cut",
        f"--nb_cores", f"4",
        f"--patch_size", f"10000",
        f"--slope", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_SLOPE_crop_cut.tif",
        f"--aspect", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_ASPECT_crop_cut.tif",
        f"--save_fld",
        f"--verbose"
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stderr)

    compare_files(reference_dir = f"{eolabtools_paths.plotor_ref}/2017_final_cut",
                  output_dir = f"{eolabtools_paths.plotor_outdir}/2017_final_cut",
                  tool = "DetecOrCult")

@pytest.mark.ci
def test_plot_orientation_opensource(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    command = [
        f"python",
        f"src/eolabtools/detection_orientation_culture/orientation_detection.py",
        f"--img", f"{eolabtools_paths.plotor_datadir}/LeHavre_2023_mosaic_crop_cut.tif",
        f"--type", f"tif",
        f"--rpg", f"{eolabtools_paths.plotor_datadir}/RPG/RPG_LeHavre_2023_cropped.shp",
        f"--output_dir", f"{eolabtools_paths.plotor_outdir}/2023_final_cut",
        f"--nb_cores", f"4",
        f"--patch_size", f"10000",
        f"--slope", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_SLOPE_crop_cut.tif",
        f"--aspect", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_ASPECT_crop_cut.tif",
        f"--save_fld",
        f"--verbose"
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stderr)

    compare_files(reference_dir = f"{eolabtools_paths.plotor_ref}/2023_final_cut",
                  output_dir = f"{eolabtools_paths.plotor_outdir}/2023_final_cut",
                  tool = "DetecOrCult")
