# -*- coding: utf-8 -*-
"""
    Setup file for rastertools.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.0.2.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
from setuptools import setup, find_packages


# Function to read requirements.txt
def read_requirements(filenames : list):
    lines = []
    for filename in filenames:
        with open(filename, "r") as file:
            lines.extend(
                line.strip()
                for line in file
                if line.strip() and not line.strip().startswith("#")
            )
    return lines


if __name__ == "__main__":
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            long_description = fh.read()

        setup(name='eolabtools',
              version="0.0.0",
              description="Collection of tools for satellite imagery analysis",
              long_description=long_description,
              long_description_content_type="text/x-rst",
              classifiers=[],
              keywords='',
              author=u"see AUTHORS.txt file",
              author_email="",
              url="https://github.com/CNES/eolabtools",
              packages=find_packages(where="src"),
              package_dir={"": "src"},
              include_package_data=True,
              zip_safe=False,
              setup_requires = ["setuptools_scm"],
              install_requires=read_requirements(["src/eolabtools/sun_map_generation/requirements.yml"]),
              # "src/eolabtools/sun_map_generation/requirements.yml",
              # "src/eolabtools/night_osm_registration/requirements.yml",
              # "src/eolabtools/detection_orientation_culture/environment.yml"
              python_requires='>=3.8.13',
              use_scm_version={"version_scheme": "no-guess-dev"},
              entry_points={
                  "console_scripts": [
                      "night_osm_image_registration = eolabtools.night_osm_registration.register_image:main",
                      "night_osm_vector_registration = eolabtools.night_osm_registration.register_vector:main",
                  ],
              },
              )
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
