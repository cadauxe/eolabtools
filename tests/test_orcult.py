from conftest import EOLabtoolsTestsPath
import subprocess
from test_utils import compare_files
import pytest
import os

# Ensure coverage starts in subprocesses
os.environ['COVERAGE_PROCESS_START'] = '.coveragerc'

# def test_plot_orientation(eolabtools_paths: EOLabtoolsTestsPath) -> None:
#     """
#     TO DO
#     """
#     command = [
#         f"python",
#         f"src/eolabtools/detection_orientation_culture/orientation_detection.py",
#         f"--img", f"{eolabtools_paths.plotor_datadir}/LeHavre_2017_mosaic_crop.tif",
#         f"--type", f"tif",
#         f"--rpg", f"{eolabtools_paths.plotor_datadir}/RPG/RPG_LeHavre_2017.shp",
#         f"--output_dir", f"{eolabtools_paths.plotor_outdir}/2017_final",
#         f"--nb_cores", f"4",
#         f"--patch_size", f"10000",
#         f"--slope", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_SLOPE_crop.tif",
#         f"--aspect", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_ASPECT_crop.tif",
#         f"--save_fld",
#         f"--verbose"
#     ]
#
#     result = subprocess.run(command, capture_output=True, text=True, check=True)
#     print(result.stderr)
#
#     compare_files(reference_dir = f"{eolabtools_paths.plotor_ref}/2017_final",
#                   output_dir = f"{eolabtools_paths.plotor_outdir}/2017_final",
#                   tool = "DetecOrCult")

# @pytest.mark.ci
# def test_plot_orientation_cut(eolabtools_paths: EOLabtoolsTestsPath) -> None:
#     """
#     TO DO
#     """
#     command = [
#         f"python",
#         f"src/eolabtools/detection_orientation_culture/detection_orientation_culture/orientation_detection.py",
#         f"--img", f"{eolabtools_paths.plotor_datadir}/LeHavre_2017_mosaic_crop_cut.tif",
#         f"--type", f"tif",
#         f"--rpg", f"{eolabtools_paths.plotor_datadir}/RPG/RPG_LeHavre_2017_cropped_bigger.shp",
#         f"--output_dir", f"{eolabtools_paths.plotor_outdir}/2017_final_cut",
#         f"--nb_cores", f"4",
#         f"--patch_size", f"10000",
#         f"--slope", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_SLOPE_crop_cut.tif",
#         f"--aspect", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_ASPECT_crop_cut.tif",
#         f"--min_nb_line_per_parcel", f"20",
#         f"--min_len_line", "8",
#         f"--save_fld",
#         f"--verbose"
#     ]
#
#     result = subprocess.run(command, capture_output=True, text=True, check=True)
#     print(result.stderr)
#
#     compare_files(reference_dir = f"{eolabtools_paths.plotor_ref}/2017_final_cut",
#                   output_dir = f"{eolabtools_paths.plotor_outdir}/2017_final_cut",
#                   tool = "DetecOrCult")

@pytest.mark.ci
def test_plot_orientation_bd_ortho1(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    if not os.path.exists(f"{eolabtools_paths.plotor_outdir}/2023_ortho1"):
        os.makedirs(f"{eolabtools_paths.plotor_outdir}/2023_ortho1")

    command = [
        f"python",
        f"src/eolabtools/detection_orientation_culture/detection_orientation_culture/orientation_detection.py",
        f"--img", f"{eolabtools_paths.plotor_datadir}/LeHavre_BD_ortho1.jp2",
        f"--type", f"jp2",
        f"--rpg", f"{eolabtools_paths.plotor_datadir}/RPG/RPG_LeHavre_2023_ortho1.shp",
        f"--output_dir", f"{eolabtools_paths.plotor_outdir}/2023_ortho1",
        f"--nb_cores", f"4",
        f"--patch_size", f"10000",
        f"--slope", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_SLOPE_crop_ortho1.tif",
        f"--aspect", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_ASPECT_crop_ortho1.tif",
        f"--min_nb_line_per_parcel", f"20",
        f"--min_len_line", "8",
        f"--save_fld",
        f"--verbose"
    ]
    print(" ".join(command))
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stderr)

    compare_files(reference_dir = f"{eolabtools_paths.plotor_ref}/2023_ortho1",
                  output_dir = f"{eolabtools_paths.plotor_outdir}/2023_ortho1",
                  tool = "DetecOrCult")


# @pytest.mark.ci
# def test_plot_orientation_bd_ortho_dir(eolabtools_paths: EOLabtoolsTestsPath) -> None:
#     """
#     TO DO
#     """
#     if not os.path.exists(f"{eolabtools_paths.plotor_outdir}/2023_ortho_dir"):
#         os.makedirs(f"{eolabtools_paths.plotor_outdir}/2023_ortho_dir")
#
#     command = [
#         f"python",
#         f"src/eolabtools/detection_orientation_culture/detection_orientation_culture/orientation_detection.py",
#         f"--img", f"{eolabtools_paths.plotor_datadir}/LeHavre_BD_ortho_dir",
#         f"--type", f"jp2",
#         f"--rpg", f"{eolabtools_paths.plotor_datadir}/RPG/RPG_LeHavre_2023_ortho1.shp",
#         f"--output_dir", f"{eolabtools_paths.plotor_outdir}/2023_ortho_dir",
#         f"--nb_cores", f"4",
#         f"--patch_size", f"10000",
#         f"--slope", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_SLOPE_crop_ortho1.tif",
#         f"--aspect", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_ASPECT_crop_ortho1.tif",
#         f"--min_nb_line_per_parcel", f"20",
#         f"--min_len_line", "8",
#         f"--save_fld",
#         f"--verbose"
#     ]
#     print(" ".join(command))
#     result = subprocess.run(command, capture_output=True, text=True, check=True)
#     print(result.stderr)
#
#     compare_files(reference_dir = f"{eolabtools_paths.plotor_ref}/2023_ortho_dir",
#                   output_dir = f"{eolabtools_paths.plotor_outdir}/2023_ortho_dir",
#                   tool = "DetecOrCult")


@pytest.mark.ci
def test_plot_orientation_bd_ortho1_normalize(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    if not os.path.exists(f"{eolabtools_paths.plotor_outdir}/2023_ortho1_normalize"):
        os.makedirs(f"{eolabtools_paths.plotor_outdir}/2023_ortho1_normalize")

    command = [
        f"python",
        f"src/eolabtools/detection_orientation_culture/detection_orientation_culture/orientation_detection.py",
        f"--img", f"{eolabtools_paths.plotor_datadir}/LeHavre_BD_ortho1.jp2",
        f"--type", f"jp2",
        f"--rpg", f"{eolabtools_paths.plotor_datadir}/RPG/RPG_LeHavre_2023_ortho1.shp",
        f"--output_dir", f"{eolabtools_paths.plotor_outdir}/2023_ortho1_normalize",
        f"--nb_cores", f"4",
        f"--normalize",
        f"--slope", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_SLOPE_crop_ortho1.tif",
        f"--aspect", f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_ASPECT_crop_ortho1.tif",
        f"--min_nb_line_per_parcel", f"20",
        f"--min_len_line", "8",
        f"--save_fld",
        f"--verbose"
    ]
    print(" ".join(command))
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stderr)

    compare_files(reference_dir = f"{eolabtools_paths.plotor_ref}/2023_ortho1_normalize",
                  output_dir = f"{eolabtools_paths.plotor_outdir}/2023_ortho1_normalize",
                  tool = "DetecOrCult")
