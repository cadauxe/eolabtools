# Calcul de l'orientation des cultures

L'orientation des cultures est une thématique commune à différents projets.


## Fichiers de code contenus dans le répertoire

- `detection_orientation_culture/orientation_detection.py`: code pour détecter l'orientation des cultures à l'aide de l'algorithme de détection de segment pylsd.
- `detection_orientation_culture/line_detection_lsdcmla.py` : code de détection de segments avec l'algorithme LSD CMLA.
- `detection_orientation_culture/detect_orientation_qsub.sh` : script qsub permettant de lancer un job sur le cluster pour le calcul de la détection des orientations à l'aide pylsd.
- `detection_orientation_culture/lsd_cmla_qsub.sh` : script qsub permettant de lancer un job sur le cluster pour le calcul de la détection des lignes avec l'algorithme LSD CMLA.


# En utilisant les scripts qsub :

## Détection de l'orientation des cultures avec pylsd

Pour obtenir l'orientation des cultures dans un fichier shapefile, il faut utiliser le script `detect_orientation_qsub.sh`.

```
python orientation_detection.py --img path/to/image_file_or_directory
                                --type extension_file_type
                                --rpg path/to/rpg_file.shp \
                                --out_shp path/to/output_file.shp \
                                --out_csv path/to/output_file.csv \
                                --nb_cores 12 \
                                --patch_size 10000 \
                                --slope path/to/slope_file.tif \
                                --aspect path/to/aspect_file.tif
```

- Le code s'appuie sur l'algorithme ```pylsd``` pour détecter les segments dans les images à partir desquels sont calculées les orientations de chacune des parcelles du RPG en entrée.

- Pour exécuter le code en parallèle, choisir ```--nb_cores```>1. 

- Si la ou les images en entrée sont de grandes tailles, il est conseillé de définir une ```--patch_size``` qui sera utilisée pour réaliser un traitement par patch (plus rapide grâce à la parallélisation).

- Les orientations extraites seront stockées dans ```--out_shp```

- Le fichier ```--out_csv``` contiendra un résumé des temps d'exécution du code ainsi que du nombre de détections.

- Les fichiers ```--slope``` et ```--aspect``` doivent être générés au préalable (cf. *Calcul des données utilisées dans le calcul des orientations*) et fournis en entrée.

## Détection de l'orientation des cultures avec LSD CMLA

### A. Extraction des lignes dans les parcelles avec l'algorithme LSD CMLA :


Avec le script `lsd_cmla_qsub.sh`.

Un exemple avec une seule image en entrée: 
```
python lsd_cmla.py --img /work/OT/eolab/DATA/BD_ORTHO/BDO_RVB_0M50_LAMB93_D11_2015.tif \
                    --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude_0M50_lsdcmla.shp
```

Un exemple avec un dossier contenant les images entrée:
```
python lsd_cmla.py --img /work/OT/eolab/DATA/BD_ORTHO/BDORTHO_2-0_RVB-0M50_JP2-E080_LAMB93_D011_2015-01-01/BDORTHO/1_DONNEES_LIVRAISON_2016-05-00226/BDO_RVB_0M50_JP2-E080_LAMB93_D11-2015 \
                    --out_shp /work/OT/eolab/taradelj/detection_orientation_culture/detection_orientation_culture/outputs/Aude_0M50_lsdcmla.shp \
                    --type jp2
```
Il faut alors préciser l'extension des fichiers images avec l'option ```--type```.

### B. Utilisation des lignes extraites pour calculer l'orientation des cultures dans les parcelles

#### Merge des shapefile issus de LSD CMLA

Avec QGIS via `Vector -> Data Management Tool -> Merge Vector Layers`.

#### Intersection entre le fichier créé à l'instant (merge de LSD CMLA) et les parcelles de RPG

Avec QGIS `Vector -> Geoprocessing tools -> Intersection`.
Le but est d'avoir les lignes LSD uniquement dans les parcelles de RPG. Le shapefile des lignes obtenus doit obtenir la colonne contenant l'ID des parcelles du RPG pour que le calcul d'orientation fonctionne.

### Calcul des orientations

TO DO

# Sans utiliser les scripts qsub (vivement déconseillé) :

Attention, l'environnements conda de l'un n'est pas compatible avec celui de l'autre, il faut donc utiliser 2 fenêtres différentes pour lancer les différentes fonctions, si les script qsub ne sont pas utilisés.

## Etapes de l'algorithme et environnement conda à utiliser

Cet algorithme se base sur l'algorithme LineSegmentDetection LSD CMLA de l'OTB pour détecter les lignes dans les images. Ensuite, différents traitements sont appliqués sur les lignes afin de calculer l'orientation globale de la culture pour chaque parcelle.

Voici les étapes de l'algorithme :



### A. Extraction des lignes dans les parcelles avec l'algorithme LSD CMLA :

#### a. Environnement conda

Il faut avoir au préalable installé le module LSD CMLA (dans l'OTB de base il n'y a que le module LSD qui est beaucoup moins efficace). Voir avec Yannick Tanguy si besoin pour l'installation.

Une fois installé il faut le lancer. Par exemple dans ma session avec une nouvelle fenêtre de terminal je fais les étapes suivantes :

```
cd /work/OT/eolab/guntzbp/build/LSD
module load otb/7.0
. ~/bin/envOTBapp.sh
cd repertoire/ou/est/situe/le/code/a/lancer
```

#### b. Commande ou fonction à lancer/utiliser

Se fait avec la fonction `lineSegmentDetection_CMLA()` dans le fichier `parcelle_orientation.py`.
On obtient en sortie un shp contenant les lignes globalement dans l'image. Ces lignes seront intersectées avec les parcelles dans l'étape suivante, pour ne garder que les lignes qui se trouvent à l'intérieur des parcelles.

Il faut modifier selon les besoins les chemins d'accès aux données (RPG, images, shp de sortie...) qui sont pour le moment en dur dans le code.


### B. Utilisation des lignes extraites pour calculer l'orientation des cultures dans les parcelles

#### a. Environnement conda

Celui de l'eolab :
```
module load conda
conda activate /softs/projets/eolab/conda/eolab
```

#### b. Commande ou fonction à lancer/utiliser


Il faut en premier lieu récupérer les informations issues du MNT pour récupérer la pente moyenne et l'orientation moyenne de la pente sur chaque parcelle. 
Pour créer le MNT monolithique pour un département donnée (ici le 11 : l'Aude), utiliser la commande `gdalbuildvrt` :

```
gdalbuildvrt -a_srs EPSG:2154 RGE_ALTI_11_5m.vrt /work/datalake/static_aux/MNT/RGEALTI_5M_France/1_DONNEES_LIVRAISON_2020-04-00197/RGEALTI_MNT_5M_ASC_LAMB93_IGN69_D011/*.asc 
```

On peut ensuite calculer l'angle de la pente ainsi que l'orientation de la pente dans deux rasters avec `gdaldem` :

```
# gdaldem slope : donne sur chaque pixel la valeur de la pente du MNT en degrés
gdaldem slope of GTiff RGE_ALTI_11_5m.vrt  RGE_ALTI_11_5m_SLOPE.tif 

# gdaldem aspect: donne sur chaque pixel la valeur de l'orientation la pente du MNT en angle azimut (Nord = 0°, Est = 90°, Sud = 180°, Ouest = 270 °).
gdaldem aspect of GTiff RGE_ALTI_11_5m.vrt  RGE_ALTI_11_5m_ASPECT.tif 
```
Ces rasters seront utilisés dans le traitement final calculant l'orientation des parcelles.

La dernière étape avant de lancer la fonction qui calcule l'orientation des parcelles est de calculer l'intersection entre les lignes détectées par l'algo LSD CMLA et le RPG. Cette étape est nécessaire. Pour faire cela, utiliser la fonction `intersection_RPG_lines()` du fichier `parcelle_processing.py` ; la sortie de cette fonction peut être utilisée comme entrée de la fonction finale `intersection_RPG_lines_polygone_per_polygon()` pour le paramètre de lignes détectées par LSD CMLA.


La dernière étape consiste à utiliser la fonction `intersection_RPG_lines_polygone_per_polygon()` du fichier `parcelle_processing.py` afin de calculer l'orientation des cultures et les différents indicateurs.
Il faut modifier selon les besoins les chemins d'accès aux données (RPG, images, shp de sortie...) qui sont pour le moment en dur dans le code.


Cette fonction combine les différentes étapes pour calculer l'orientation de chaque parcelle de culture :

Pour chaque parcelle : 

1. On récupère les lignes qui correspondent à la parcelle ;
2. Si le **nombre de lignes contenues dans une parcelle est inférieur à un nombre donné** (pour le moment fixé à 40), on ne sait pas donner l'orientation de la parcelle (trop incertaine) et on passe à la parcelle suivante. Sinon, on continue de travailler dans la parcelle actuelle :
3. Une ligne = un trait entre un point A=(xa, ya) et B=(xb,yb). Pour chaque ligne on calcule le vecteur AB = (xb-xa, yb-ya) qu'on normalise. 
4. Une fois qu'on a toutes les coordonnées des vecteurs normalisés de la parcelle, on souhaite supprimer les outliers. On utilise pour cela l'indicateur **IQR = Q3 - Q1**, avec Q1 = 1er quartile et Q3 = 3ème quartile. La règle "standard" qui définie les outliers est la suivante : **les valeurs en dessous de Q1-1.5\*IQR ou au-dessus et Q3+1.5\*IQR sont considérées comme des outliers**. Si un vecteur normalisé possède une coordonnée en x ou en y identifiée comme outlier, il est supprimé de la liste des vecteurs.
5. La **norme des vecteurs restants est ensuite vérifiée : si elle est inférieure à un seuil donné (fixé ici à 8 pour la vigne), on ne prend pas en compte le vecteur**. On s'affranchit ainsi des petites lignes qui sont en bordure de parcelle et qui perturbent l'orientation globale.
6. Une fois tous les vecteurs de la parcelle triés, on fait la médiane des déplacements ce qui nous donne (xmed, ymed).
7. On calcule le centroide de la parcelle (xc, yc).
8. Le segment qui représente visuellement l'orientation de la vigne est centré sur le centroide et relie les points (xc-xmed, yc-ymed) et (xc+xmed, yc+ymed). Pour plus de visibilité (segments plus grands), un facteur A assez conséquent a été rajouté : (xc-A * xmed, yc-A * ymed) et (xc+A * xmed, yc+A * ymed).

On peut représenter ces différentes étapes sous forme de schéma :

<img src="imgs/shema_code_calcul_orientation.PNG"  width="900">


De plus pour chaque orientation calculée, 4 colonnes de d'indicateur de qualités sur l'orientation calculée ont été ajoutées :

- "NB_LINES" qui totalise le nombre de lignes détectées prises en compte dans le calcul de l'orientation (plus on a de lignes et plus l'orientation calculée est fiable) ;
- "MEAN_LINES" qui donne la longueur moyenne des lignes prises en compte (plus les lignes sont longues et plus on a de chances qu'elles soient pertinentes dans le calcul de l'orientation).
- Les colonnes "STD_X_COOR" et "STD_Y_COOR" qui donnent l'écart-type des coordonnées en x et en y des lignes normalisées.
 
A partir des rasters Aspect et Slope calculés auparavent on peut extraire la valeur moyenne des pixels de ces éléments pour chaque parcelle. Ces valeurs moyennes ont été ajoutées dans des colonnes du shapefile :
- "SLOPE" qui indique l'angle moyen de la pente en degrés ;
- "ASPECT" qui indique l'orientation moyenne de la pente en degrés (angle azimut).
- "CALC_ASPECT" qui est la conversion en angle azimut du vecteur calculé de l'orientation des cultures, afin d epouvoir comparer l'orientation de la pente avec celle des cultures.

Enfin une colonne "INDIC_ORIE" a été ajoutée ; il s'agit d'un indicatur d'orientation allant de 0 à 90. 0=les rangées des cultures sont dans le sens de la pente ; 90=les orientations sont perpendiculaires.

## Calcul des données utilisées dans le calcul des orientations


Il faut en premier lieu récupérer les informations issues du MNT pour récupérer la pente moyenne et l'orientation moyenne de la pente sur chaque parcelle. 
Pour créer le MNT monolithique pour un département donnée (ici le 11 : l'Aude), utiliser la commande `gdalbuildvrt` :

```
gdalbuildvrt -a_srs EPSG:2154 RGE_ALTI_11_5m.vrt /work/datalake/static_aux/MNT/RGEALTI_5M_France/1_DONNEES_LIVRAISON_2020-04-00197/RGEALTI_MNT_5M_ASC_LAMB93_IGN69_D011/*.asc 
```

On peut ensuite calculer l'angle de la pente ainsi que l'orientation de la pente dans deux rasters avec `gdaldem` :

```
# gdaldem slope : donne sur chaque pixel la valeur de la pente du MNT en degrés
gdaldem slope of GTiff RGE_ALTI_11_5m.vrt  RGE_ALTI_11_5m_SLOPE.tif 

# gdaldem aspect: donne sur chaque pixel la valeur de l'orientation la pente du MNT en angle azimut (Nord = 0°, Est = 90°, Sud = 180°, Ouest = 270 °).
gdaldem aspect of GTiff RGE_ALTI_11_5m.vrt  RGE_ALTI_11_5m_ASPECT.tif 
```
Ces rasters seront utilisés dans le traitement final calculant l'orientation des parcelles.