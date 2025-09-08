Contributing
============

Thanks for helping to build eolabtools!

Report issues or bugs
~~~~~~~~~~~~~~~~~~~~~

If you encounter a bug, unexpected behavior, or see something that could be improved:

* Open an issue on the GitHub Issues page,
* Describe the problem clearly, with a minimal reproducible example if possible,
* Indicate the version of Eolabtools, Python, and platform you’re using.

Bug reports, feature suggestions, and usability feedback are all welcome.

Seek support or ask questions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have questions about how to use Eolabtools:

* First, check the documentation,
* If your question isn't answered there, post your question in the Issues with the label question.

We aim to respond as quickly as possible and encourage community help.

Retrieve the code: forking and cloning the Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make a fork of the `eolabtools repository <https://github.com/CNES/eolabtools>`__ and clone
the fork.

A documentation is available on GitHub to help platform users create a fork: `https://docs.github.com/fork-a-repo <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo>`__

.. code-block:: none

   git clone https://github.com/<your-github-username>/eolabtools.git
   cd eolabtools

You may want to add ``https://github.com/CNES/eolabtools`` as an upstream remote
repository.

.. code-block:: none

   git remote add upstream https://github.com/CNES/eolabtools

Building Eolabtools
~~~~~~~~~~~~~~~~~~~

Eolabtools is a pure-python repository and each tools can be use in separate virtual environnements. Development installation should
be as simple as cloning the repository and running the following in the cloned directory:

**For SunMapGeneration :**

.. code-block:: console

    conda create -n sunmap_env python=3.12 libgdal=3.5.0 -c conda-forge -c defaults -y
    conda activate sunmap_env
    pip install georastertools --no-binary rasterio
    pip install ".[SunMapGen]" --force-reinstall --no-cache-dir

**For NightOsmRegistration :**

.. code-block:: console

    conda create -n nightosm_env python=3.12 libgdal=3.11.0 markupsafe -c conda-forge
    conda activate nightosm_env
    pip install ".[NightOsmReg]"

**For DetectionOrientationCulture :**

.. code-block:: console

    conda create -n orcult_env python=3.12 libgdal=3.11.0 -c conda-forge -c defaults -y
    conda activate orcult_env
    pip install -e ".[DetecOrCult]"

If you have any trouble, please open an issue on the
`eolabtools issue tracker <https://github.com/CNES/eolabtools/issues>`_.

Running tests
~~~~~~~~~~~~~

Eolabtools uses `pytest <https://docs.pytest.org/en/latest/>`_ for testing. You
can run tests from the main eolabtools directory for the tool you installed as follows:

.. code-block:: none

    pytest tests/test_sunmap.py #For SunMapGeneration
    pytest tests/test_nightosm.py #For NightOsmRegistration
    pytest tests/test_orcult.py #For DetectionOrientationCulture

Coverage
~~~~~~~~

It is possible to check code coverage

.. code-block:: none

    pytest tests/test_sunmap.py --cov=src/eolabtools/sun_map_generation --cov-report=html #For SunMapGeneration
    pytest tests/test_nightosm.py --cov=src/eolabtools/night_osm_registration --cov-report=html #For NightOsmRegistration
    pytest tests/test_orcult.py --cov=src/eolabtools/detection_orientation_culture --cov-report=html #For DetectionOrientationCulture

You can still use all the usual pytest command-line options in addition to those.

Documentation
~~~~~~~~~~~~~

We use `numpydoc <http://numpydoc.readthedocs.io/en/latest/format.html>`_ for our docstrings.

Building the docs is possible with

.. code-block:: none

   $ conda create -n eolabtools_doc python=3.12 sphinx_rtd_theme sphinxcontrib-bibtex
   $ conda activate eolabtools_doc
   $ sphinx-build -b html docs/source docs/build
