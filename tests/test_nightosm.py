from conftest import EOLabtoolsTestsPath
from src.eolabtools.night_osm_registration.register_image import night_osm_image_registration
from src.eolabtools.night_osm_registration.register_vector import night_osm_vector_registration
from test_utils import compare_files, clear_outdir, create_outdir, fill_config_nightosm
import pytest
import yaml
import os


@pytest.mark.ci
def test_nightosm_rasterize_radiance(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    fill_config_nightosm(f"{eolabtools_paths.nightosm_datadir}/config/config1.yml", eolabtools_paths)
    create_outdir(f"{eolabtools_paths.nightosm_outdir}/test_nightosm_rasterize_radiance")

    config = f"{eolabtools_paths.nightosm_datadir}/config/config1.yml"
    osm_config = f"{eolabtools_paths.nightosm_datadir}/osm-config/osm_config_subtracted.yml"
    with open(config) as f:
        config = yaml.safe_load(f)
    with open(osm_config) as f:
        osm_tags = yaml.safe_load(f)
    settings = {
        "infile":f"{eolabtools_paths.nightosm_datadir}/Extrait1/Extract1-Radiance.tif",
        "outdir":f"{eolabtools_paths.nightosm_outdir}/test_nightosm_rasterize_radiance/",
    }
    settings = settings | config
    settings["osm_tags"] = osm_tags

    night_osm_image_registration(**settings)

    compare_files(reference_dir = f"{eolabtools_paths.nightosm_ref}/TestRasterizeRadiance",
                  output_dir = f"{eolabtools_paths.nightosm_outdir}/test_nightosm_rasterize_radiance",
                  tool = "NightOSM")
    clear_outdir(f"{eolabtools_paths.nightosm_outdir}/test_nightosm_rasterize_radiance")


@pytest.mark.ci
def test_nightosm_rasterize_rgb(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    fill_config_nightosm(f"{eolabtools_paths.nightosm_datadir}/config/config2.yml", eolabtools_paths)
    create_outdir(f"{eolabtools_paths.nightosm_outdir}/test_nightosm_rasterize_rgb")

    config = f"{eolabtools_paths.nightosm_datadir}/config/config2.yml"
    osm_config = f"{eolabtools_paths.nightosm_datadir}/osm-config/osm_config_subtracted.yml"
    with open(config) as f:
        config = yaml.safe_load(f)
    with open(osm_config) as f:
        osm_tags = yaml.safe_load(f)
    settings = {
        "infile": f"{eolabtools_paths.nightosm_datadir}/Extrait2/Extract2-FakeRGB.tif",
        "outdir": f"{eolabtools_paths.nightosm_outdir}/test_nightosm_rasterize_rgb/",
    }
    settings = settings | config
    settings["osm_tags"] = osm_tags

    night_osm_image_registration(**settings)

    compare_files(reference_dir=f"{eolabtools_paths.nightosm_ref}/TestRasterizeRGB",
                  output_dir=f"{eolabtools_paths.nightosm_outdir}/test_nightosm_rasterize_rgb",
                  tool="NightOSM")
    clear_outdir(f"{eolabtools_paths.nightosm_outdir}/test_nightosm_rasterize_rgb")


@pytest.mark.ci
def test_nightosm_register_radiance(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    fill_config_nightosm(f"{eolabtools_paths.nightosm_datadir}/config/config3.yml", eolabtools_paths)
    create_outdir(f"{eolabtools_paths.nightosm_outdir}/test_nightosm_register_radiance")

    config = f"{eolabtools_paths.nightosm_datadir}/config/config3.yml"
    osm_config = f"{eolabtools_paths.nightosm_datadir}/osm-config/osm_config_subtracted.yml"
    with open(config) as f:
        config = yaml.safe_load(f)
    with open(osm_config) as f:
        osm_tags = yaml.safe_load(f)
    settings = {
        "infile": f"{eolabtools_paths.nightosm_datadir}/Extrait1/Extract1-Radiance.tif",
        "outdir": f"{eolabtools_paths.nightosm_outdir}/test_nightosm_register_radiance/",
        "auxfiles": [f"{eolabtools_paths.nightosm_datadir}/Extrait1/Extract1-FakeRGB.tif"],
    }
    settings = settings | config
    settings["osm_tags"] = osm_tags

    night_osm_image_registration(**settings)

    compare_files(reference_dir=f"{eolabtools_paths.nightosm_ref}/TestRegisterRadiance",
                  output_dir=f"{eolabtools_paths.nightosm_outdir}/test_nightosm_register_radiance",
                  tool="NightOSM")
    clear_outdir(f"{eolabtools_paths.nightosm_outdir}/test_nightosm_register_radiance")


@pytest.mark.ci
def test_nightosm_register_rgb(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    fill_config_nightosm(f"{eolabtools_paths.nightosm_datadir}/config/config4.yml", eolabtools_paths)
    create_outdir(f"{eolabtools_paths.nightosm_outdir}/test_nightosm_register_rgb")

    config = f"{eolabtools_paths.nightosm_datadir}/config/config4.yml"
    osm_config = f"{eolabtools_paths.nightosm_datadir}/osm-config/osm_config_subtracted.yml"
    with open(config) as f:
        config = yaml.safe_load(f)
    with open(osm_config) as f:
        osm_tags = yaml.safe_load(f)
    settings = {
        "infile": f"{eolabtools_paths.nightosm_datadir}/Extrait2/Extract2-FakeRGB.tif",
        "outdir": f"{eolabtools_paths.nightosm_outdir}/test_nightosm_register_rgb/",
    }
    settings = settings | config
    settings["osm_tags"] = osm_tags

    night_osm_image_registration(**settings)

    compare_files(reference_dir=f"{eolabtools_paths.nightosm_ref}/TestRegisterRGB",
                  output_dir=f"{eolabtools_paths.nightosm_outdir}/test_nightosm_register_rgb",
                  tool="NightOSM")
    clear_outdir(f"{eolabtools_paths.nightosm_outdir}/test_nightosm_register_rgb")

@pytest.mark.ci
def test_nightosm_vector(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    create_outdir(f"{eolabtools_paths.nightosm_outdir}/test_nightosm_vector")

    night_osm_vector_registration(
        vector=f"{eolabtools_paths.nightosm_datadir}/Extrait2/Extract2_RadiancePeaks.gpkg",
        grid=f"{eolabtools_paths.nightosm_datadir}/Extrait2/Extract2-displacement_grid.tif",
        outdir=f"{eolabtools_paths.nightosm_outdir}/test_nightosm_vector/",
        name="Extract2_radiance_peaks_shifted"
    )

    compare_files(reference_dir=f"{eolabtools_paths.nightosm_ref}/TestRegisterVector",
                  output_dir=f"{eolabtools_paths.nightosm_outdir}/test_nightosm_vector",
                  tool="NightOSM")
    clear_outdir(f"{eolabtools_paths.nightosm_outdir}/test_nightosm_vector")


@pytest.mark.ci
def test_nightosm_simple_config(eolabtools_paths: EOLabtoolsTestsPath) -> None:
    """
    TO DO
    """
    fill_config_nightosm(f"{eolabtools_paths.nightosm_datadir}/config/config5.yml", eolabtools_paths)
    create_outdir(f"{eolabtools_paths.nightosm_outdir}/test_nightosm_simple_config")

    config = f"{eolabtools_paths.nightosm_datadir}/config/config5.yml"
    osm_config = f"{eolabtools_paths.nightosm_datadir}/osm-config/osm_config_simple.yml"
    with open(config) as f:
        config = yaml.safe_load(f)
    with open(osm_config) as f:
        osm_tags = yaml.safe_load(f)
    settings = {
        "infile": f"{eolabtools_paths.nightosm_datadir}/Extrait2/Extract2-FakeRGB.tif",
        "outdir": f"{eolabtools_paths.nightosm_outdir}/test_nightosm_simple_config/",
    }
    settings = settings | config
    settings["osm_tags"] = osm_tags

    night_osm_image_registration(**settings)

    compare_files(reference_dir=f"{eolabtools_paths.nightosm_ref}/TestSimpleConfig",
                  output_dir=f"{eolabtools_paths.nightosm_outdir}/test_nightosm_simple_config",
                  tool="NightOSM")
    clear_outdir(f"{eolabtools_paths.nightosm_outdir}/test_nightosm_simple_config")
