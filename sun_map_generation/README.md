# sun_map_generation

Outil permettant de générer des cartes d'ensoleillement pour une zone et un instant précis

## Installing environment

Pour installer toutes les librairies nécessaires, lancer les commandes suivantes : 

```
ml conda
conda env create -f requirements.yml
conda activate carte_enso
```

## Content

- `/listings` : Ce dossier contient les fichiers de listing (`.lst`) où sont listés les chemins vers les MNS (ici Paris 2021)

_listing_test.lst_ :
```
/work/EOLAB/DATA/MNS/Paris/75-2021-0645-6863-LA93-0M50.tif
/work/EOLAB/DATA/MNS/Paris/75-2021-0646-6863-LA93-0M50.tif
/work/EOLAB/DATA/MNS/Paris/75-2021-0647-6863-LA93-0M50.tif
```

- `/notebooks` : contient des notebooks de test et de visualisation

- `/src` : contient les scripts principaux :

    - `SunMapGenerator.py` : fichier python principal
    - `sun_map_script.slurm` : script slurm qui appelle le script principal. Permet de paramétrer ses besoins et d'attribuer la quantité de ressources nécessaires


## Run the tool

Pour lancer l'outil, il faut utiliser le script slurm : 
```
sbatch sun_map_script.slurm
```

## Les données en entrée

_sun_map_script.slurm_ :

```
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
```

- `digital_surface_model` : chemin vers le fichier `.lst`
- `area` : Nom de la ville où appliquer le calcul d'ensoleillement
- `date` : Date ou plage de dates (YYYY-MM-DD) et pas (en jours). La valeur du pas par défaut est 1 jour
- `time` : Horaire ou plage horaires (HH:MM) et pas (en minutes). La valeur du pas par défaut est 30 minutes
- `occ_changes` : Limite de changement soleil/ombre d'un pixel sur une journée. Chiffre pair (2 ou 4). Valeur par défaut 4.
- `nb_cores` : Pour lancer le traitement en parallèle. Nombre de processus à renseigner.
- `output_dir` : chemin vers le répertoire de sortie
- `save_temp` : A renseigner pour obtenir le fichier descriptif du temps de calcul par étape de la chaîne de traitement (`processing_time.csv`)
- `save_masks` : A renseigner pour sauvegarder les masques d'ombre calculés à chaque pas horaire

## Les fichiers en sortie

Les fichiers sont stockés dans le répertoire `output_dir`

- **masques d'ombre** : _[tile_name]-hillshade-[YYYYMMDD]-[HHMM].tif_ L'algorithme les calcule pour chaque tuile, chaque jour et toute heure renseignés par l'utilisateur

- **raster pourcentage d'exposition au soleil** : _[tile_name]-sun_map-[YYYYMMDD].tif_ L'algorithme les calcule pour chaque tuile et chaque jour renseignés par l'utilisateur

- **vecteur apparition/disparition du soleil** : _[tile_name]-sun_times-[YYYYMMDD].gpkg_ L'algorithme les calcule pour chaque tuile pour le premier jour de la plage renseignée par l'utilisateur. L'utilisateur possède le choix du nombre limite de passage soleil/ombre d'un pixel pour une journée (`occ_changes`)

