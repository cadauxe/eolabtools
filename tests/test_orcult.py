from conftest import EOLabtoolsTestsPath
from src.eolabtools.detection_orientation_culture import detection_orientation_culture
from test_utils import compare_files, clear_outdir, create_outdir
import pytest
import os

# Ensure coverage starts in subprocesses
os.environ['COVERAGE_PROCESS_START'] = '.coveragerc'

@pytest.mark.ci
def test_plot_orientation_bd_ortho1(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    create_outdir(f"{eolabtools_paths.plotor_outdir}/2023_ortho1")

    detection_orientation_culture(
        img=f"{eolabtools_paths.plotor_datadir}/LeHavre_BD_ortho1.jp2",
        rpg=f"{eolabtools_paths.plotor_datadir}/RPG/RPG_LeHavre_2023_ortho1.shp",
        output_dir=f"{eolabtools_paths.plotor_outdir}/2023_ortho1",
        slope=f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_SLOPE_crop_ortho1.tif",
        aspect=f"{eolabtools_paths.plotor_datadir}/RGE_ALTI_76_5m_ASPECT_crop_ortho1.tif",
        nb_cores=4,
        type="jp2",
        normalize=False,
        save_fld=True,
        verbose=True,
        patch_size=10000,
        area_min=20000.,
        min_nb_line_per_parcel=20,
        min_len_line=8,
    )

    compare_files(reference_dir = f"{eolabtools_paths.plotor_ref}/2023_ortho1",
                  output_dir = f"{eolabtools_paths.plotor_outdir}/2023_ortho1",
                  tool = "DetecOrCult")
    clear_outdir(f"{eolabtools_paths.plotor_outdir}/2023_ortho1")

