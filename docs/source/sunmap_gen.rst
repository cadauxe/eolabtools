.. _sunmap_gen:

==================
Sun Map Generation
==================

#Change installation procedure
#TO DO

Sun Map Generation is a tool for generating sunshine maps for a specific area at a specific time.

Installing environment
======================

To install the required libraries, please launch the following commands :

.. code-block:: console

    conda create -n carte_enso
    conda activate carte_enso
    conda install python=3.8.13 libgdal=3.5.0
    pip install . (or pip install the wheel if built)
    pip install georastertools --no-binary rasterio


Content
=======


- `/src` : Contains the main scripts files :

    - `SunMapGenerator.py` : Main python file
    - `sun_map_script.slurm` : Slurm script that launches the main script. Allow to parametrize according to the needs and allocate the quantity of resources required.


Run the tool
============

To launch the tool, please use slurm script :

.. code-block:: console

    sbatch sun_map_script.slurm

Input data
==========

_sun_map_script.slurm_ :

.. code-block:: console
    #!/bin/bash
    #SBATCH --job-name=sunmap       # job's name
    #SBATCH --output=outfile-%j.out
    #SBATCH --error=errfile-%j.err
    #SBATCH -N 1                        # number of nodes (or --nodes=1)
    #SBATCH -n 32                       # number of tasks (or --tasks=8)
    #SBATCH --mem-per-cpu=8000M         # memory per core
    #SBATCH --time=01:00:00             # Wall Time
    #SBATCH --account=cnes_level2       # MANDATORY : account  ( launch myaccounts to list your accounts)
    #SBATCH --export=none               # To start the job with a clean environnement and source of ~/.bashrc

    ml conda
    conda activate /work/EOLAB/USERS/duthoit/envs/conda/crt_enso/

    cd /work/EOLAB/USERS/duthoit/CARTE_ENSOILLEMENT/src/

    python SunMapGenerator.py --digital_surface_model /work/EOLAB/USERS/duthoit/CARTE_ENSOILLEMENT/listings/listing_test.lst\
                              --area Paris \
                              --date 2024-07-20 2024-07-30 3 \
                              --time 10:00 14:00 30 \
                              --nb_cores 32 \
                              --occ_changes 4 \
                              --output_dir /work/EOLAB/USERS/duthoit/CARTE_ENSOILLEMENT/outputs/ \
                              --save_temp \
                              --save_masks


- `digital_surface_model` : path to the `.lst` file
- `area` : Name of the city where to apply the sunlight calculation
- `date` : Date or date range (YYYY-MM-DD) and step (in days). The default step value is 1 day.
- `time` : Time or time range (HH:MM) and step (in minutes). The default step value is 30 minutes.
- `occ_changes` : Limit of sun/shade change of a pixel over one day. Even number (2 or 4). Default value 4.
- `nb_cores` : To launch parallel processing. Number of processes to be entered.
- `output_dir` : Path to the output directory
- `save_temp` : To be filled in to obtain the file describing the calculation time per step in the processing chain (`processing_time.csv`).
- `save_masks` : To save shadow masks calculated at each time step

Output files
============

Files are stored in the `output_dir` directory :

- **Shadow masks** : _[tile_name]-hillshade-[YYYYMMDD]-[HHMM].tif_ The algorithm calculates them for each tile, day and time entered by the user.

- **Percentage of sun exposure raster** : _[tile_name]-sun_map-[YYYYMMDD].tif_ The algorithm calculates them for each tile and each day entered by the user.

- **Sun appearance/disappearance vector** : _[tile user can choose the number of times a pixel will be exposed to sun/shade in a given day (`occ_changes`).


