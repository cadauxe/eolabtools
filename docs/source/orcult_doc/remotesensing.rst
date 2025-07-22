.. _remotesensing:

================
More Information
================

Introduction
============

Remote sensing in the optical domain consists in measuring the sun light
reflected by Earth. That’s an indirect measurement of the ground
reflectance. On a given target, the latter can vary significantly with
the sun and observing geometries causing directional effects. When we
process and interpret reflectance variations, we do so to understand
what is happening at the Earth’s surface. Directional effects are
therefore a measurement disturbance that needs to be corrected. This can
be done using BRDF based on kernel models :cite:`roujean92`.
For this reason, space missions generating global time series of
observations are corrected to provide nadir BRDF adjusted reflectance.
This type of correction was first implemented on missions with large
fields of view, involving significant directional effects like MODIS
:cite:`schaaf2002` and VEGETATION
:cite:`HAGOLLE2005172`. Then, missions with
intermediate-sized fields of view are now also corrected, as in the case
of Landsat:cite:`ROY2016255`, sometimes by combining several
missions, each with its own observation properties, allowing for example
the generation of harmonised Sentinel-2 / Landsat products
:cite:`rs11060632`.

Very fine description of the BRDF at given crop, at given development
stage, can be obtained by modelling, for exemple with DART
:cite:`Gastellu2017`, or by field measurements
:cite:`BAI2023344`. To get a better idea of directional
effects in a cultivated area, we can consider the extreme case of the
vineyard. It’s easy to understand that, depending on the acquisition
geometry, the fraction of apparent shadow from the observation point can
be highly variable, resulting in highly variable reflectance. In
agricultural areas, to be able to understand and model the observed
scene, it’s not enough to know the position of the sun and the
observation point. One last critical parameter is missing: the crop
orientation. And since cultivated farmland accounts for one third of the
world surface area and almost 50% of the surface area of mainland
France, it’s clear that determining the orientation of crops on a very
large scale is very important for the processing and interpretation of
remote sensing images.

Knowing the orientation of crops can also be very useful beyond remote
sensing. The orientation of crops in relation to the slope of the land
contributes significantly to the risk of intense runoff and consequently
to soil erosion and sediment export by water. The prediction of runoff
flow directions on tilled fields has been studied by
:cite:`Takken2001`. Crop orientation can also be used to
understand and improve farming practices. It’s possible to optimize crop
row orientation to suppress weeds and increase crop yield as reported in
:cite:`Borger2010` or to control glyphosate-resistant
horseweed in vineyard as studied by
:cite:`alcorta_fidelibus_steenwerth_shrestha_2011`;

As crop orientation has been poorly studied
:cite:`rs10010099`, in this paper we propose a method to
determine the crop orientation from sub-metric very high resolution
remote sensing images. Tests were carried out with less well-resolved
images, but as the results were inconclusive, we do not consider this
type of image to be of interest for our work. Our method has been
developed and tested over France in representative areas and crop types.
Detecting parcels footprints is not the purpose of this paper because
there are existing databases on the subject, it is also possible to
determine the parcels footprint from the images themselves
:cite:`rs13112197`. The method is presented in detail
hereafter together with the performance and limitations obtained on a
data-set covering an overall surface area of about 50000 square
kilometers spread on 8 french departments.

Materials and Methods
=====================

Study area
----------

The study area corresponds to regions in the four corners of
metropolitan France. We selected nine different departments :
Alpes-Maritimes (06), Ariège (09), Aude (11), Côte-d’Or (21), Gers (32),
Ille-et-Vilaine (35), Jura (39), Haute-Saône (70) and Sâone-et-Loire
(71). Their selection was based on their differences in growth
conditions and cultural compositions. Figure 1 shows their
geographical location.

.. figure:: /_static/orcult/IMGS/france.png
   :alt: 
   :width: 70.0%
   :align: center

Input Data
----------

Airbone images
~~~~~~~~~~~~~~

In the context of a study requiring the identification of details within
a plot, it makes sense to look at the contribution of very high
resolution aerial images. Aerial images can be acquired using airborne
craft or satellites and have already proven their usefulness in numerous
applications such as vegetation mapping :cite:`apport_ortho`
or precision farming :cite:`precisionfarming`. In France,
IGN, the French National Geographic Institute [1]_ provides the BD ORTHO
which an opendata database of orthoreferenced images. Their goal is to
highlight the French territory and multiply the possibilities of the
projects thanks to the information provided by the exploitation and
visualization of these data. The catalogue [2]_ is updated gradually
over time with about thirty French departments surveyed over a year.
Thus, a specific area is updated at a rate of 3 or 4 years
[:ref:`appendix-a`]. The BD ORTHO now offers a very
satisfactory resolution of 20 cm, available in both visible and
near-infrared spectral range.

Satellite images
~~~~~~~~~~~~~~~~

Satellite images play a crucial role in Earth observation and gathering
geospatial data. Several space programs provide high-quality satellite
imagery for a variety of applications. Among the programs widely used
for agriculture, are Landsat, which has been providing continuous data
since 1972 :cite:`landsat`, Copernicus/Sentinels, the Earth
Observation component of the European Union’s space programme
:cite:`sentinel`, and MODIS, an instrument on board the
Terra and Aqua satellites that provides daily Earth imagery
:cite:`modis`. However, our study at the sub-parcel level
requires very high-resolution satellite imagery because the inter-row
distance can sometimes be as small as 10 cm, which these programs cannot
provide us with, see Figure 2. Pléiades is a CNES program
:cite:`pleiades` which offers very high-resolution Earth
observation images, the products are distributed by Airbus. Key features
include high resolution (50 cm panchromatic bands and 2 meters for color
ones after resampling), stereo imaging capabilities for 3D restitution,
rapid revisit time for frequent image acquisition. Its multispectral
capabilities are very usefull for land cover and vegetation analysis.
Each image covers about 20 km², with agile pointing and application
versatility in urban planning, agriculture, and more. They are already
used for agricultural field delineation
:cite:`imsat1, imsat2`, the method proposed here is very
complementary to this papers.

.. figure:: /_static/orcult/IMGS/image1.png
   :alt:
   :width: 70.0%
   :align: center

.. _RPG:

Plot footprints
~~~~~~~~~~~~~~~

The Graphic Parcel Register (GPR) or Registre Parcellaire Graphique
(RPG) in french is produced annually by the French payment agency and
IGN :cite:`rpg` at a national level. Although it is not
exhaustive, as it only lists agricultural parcels eligible for common
agricultural policy premiums, it contains an enormous number of parcels.
It is a vector layer which provides essential information on the
geometry and crop type of each of the agricultural plots listed.

.. figure:: /_static/orcult/IMGS/table1.png
   :alt:
   :width: 80.0%
   :align: center


Table 1 shows the distribution of crops by department, as described in the GPR, in the dataset used for this
study. In particular, natural areas, meadows and forests were not included. Thanks to the departments diversity, we will address a
very large number of possible cases allowing us to check the effectiveness
and relevance of the method by considering various crop conditions. Our coverage extends across a spectrum of terrains, encompassing
plains, hilly areas, and mountainous regions, as well as diverse climatic conditions found in the north, south, territories, mountains,
and coastal regions [Figure 1]. Furthermore, different crop types exhibit varying growth patterns, rates, and timing, each
with its own unique phenology meaning the time of the image acquisition will be crucial.
Additionally, spacing between rows varies depending on the crop type, but all at a sub-metric level. Thus, the diversity in terrain and
climate, along with the differing growth characteristics of various crop types, presents a complex and varied agricultural landscape.

The GPR is amended, enriched manually by all farmers. As a consequence, it is possible to find a plot geometry that does not
quite correspond to the truth of the ground. In some cases like the one in Figure 3, a geometry includes several plots
with different row orientations, this is an aspect that must be taken into account in our study.

.. figure:: /_static/orcult/IMGS/image2.png
   :alt:
   :width: 70.0%
   :align: center

Slope and aspect
~~~~~~~~~~~~~~~~

| Slope and aspect (considered as the slope direction) is critical
  information when coupled with culture row orientation. Indeed, a
  certain crop orientation combined with a strong degree of slope can
  have a significant effect on mudflows or water runoff after an heavy
  rain.
| To compute these information, we used the 5m mesh RGE ALTI Digital
  Terrain Model :cite:`manuelMNT`. Thanks to this file, we
  can retrieve the slope and aspect according to a 5m grid across the
  entire national territory. By using this information and the geometry
  of each agricultural plot in the GPR, we can deduce the average slope
  as well as its average orientation. The slope information lies between
  0° and 90° whereas its direction lies between 0° and 360°. There are
  respectively represented by :math:`\theta_1` and :math:`\theta_2` in
  Figure 4. Although these topographic measurements
  are not useful for orientation detection, we describe them here
  because they are provided as part of the data package generated for
  these paper.

.. figure:: /_static/orcult/IMGS/slope_aspect.png
   :alt:
   :width: 70.0%
   :align: center

.. _metric:

Creation of a validation dataset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

| We couldn’t find a crop orientation ground truth in France. To
  overcome this lack of information and in order to have the opportunity
  to discuss the results, it was necessary to create a one on different
  areas and on different crop types. Departments of Alpes-Maritimes,
  Côte-d’Or, Gers, Ille-et-Vilaine and Haute-Sâone have been choosen. To
  avoid any bias in the results, we maintained a consistent ratio
  between the percentage present in the GPR of the corresponding areas
  data and the ground truth data. Table 2 lists
  the number of annotated plots, and the graph in
  Figure 5 supports our intention.

.. figure:: /_static/orcult/IMGS/table2.png
   :alt:
   :width: 70.0%
   :align: center

Obviously, it is necessary to assess the legitimacy of this ground truth before being able to compare it with the results of our algorithm.

.. figure:: /_static/orcult/IMGS/image3.png
   :alt:
   :width: 70.0%
   :align: center


To do so, we manually pointed the orientation on a representative plot a hundred times, taking care to remove the
previous pointing each time. The Figure 6 shows the distribution of the orientation angle of the plot from these different
pointing. We can observe that the difference between the minimum and maximum is very small, about 2 degrees, and that the standard
deviation :math:`\sigma = 0.37` is also low. We can see on the graph that the distribution is similar to a Gaussian.
Therefore, we can say that 95% of the time we are accurate within 1.5 degrees which correponds to the +/-:math:`2\sigma` interval.


Method
------

In this section, we will present, step by step, the implemented method.
The general approach is to detect linear structures in the image, using
line segment detection tools, filter these segments and perform
statistical calculations on their orientation per parcel. Figure
7 illustrates the process we implemented.

.. _segment detect:

Segment detection
~~~~~~~~~~~~~~~~~

| Line segment detection is a fundamental task in computer vision, with
  numerous applications in robotics, autonomous driving, and image
  processing. In recent years, several state-of-the-art methods have
  been proposed to tackle this problem, achieving impressive results on
  various benchmarks.
| LSD is a highly efficient linear-time algorithm that accurately detect
  line segments in digital images
  :cite:`ipol.2012.gjmr-lsd`. It is designed to work on any
  digital image without parameter tuning. It controls its own number of
  false detections: on average, one false alarm is allowed per image.
  The method is based on Burns, Hanson, and Riseman’s method
  :cite:`pattern`, and uses an a contrario validation
  approach according to Desolneux, Moisan, and Morel’s theory
  :cite:`computer`. Moreover, LSD significantly reduces
  computation time and memory usage compared to traditional Hough
  Transform methods.
| There have been further progress in line segment detection, especially
  in the field of deep learning model. Techniques using novel deep
  convolutional models designed for real-time line segment detection
  :cite:`tplsd`. These type of model achieves competitive
  accuracy and operates at impressive real-time speeds
  :cite:`elsed`, making it well-suited for time-critical
  applications.
| Additionally, there are alternative approaches to line detection that
  aim to minimize computational requirements and improve real-time
  performance. Efficient line detection without sacrificing real-time
  performance can be achieved through the use of the Progressive
  Probabilistic Hough Transform (PPHT) algorithm
  :cite:`ppht`. Using the Randomized Hough Transform (RHT)
  process can also help reduce both computation time and memory usage
  which offers another interesting approach to line detection
  :cite:`rht`.
| During our study, we first implemented our crop orientation detection
  method by integrating the LSD method
  :cite:`ipol.2012.gjmr-lsd` since we are not constrained by
  the execution time. However, in order to deploy open source the
  method, we had to consider an alternative to the python LSD library.
  As a consequence, we decided also to use implement the
  FastLineDetector library from OpenCV, which offers a similar
  functionality. The rest of the paper will present the observed results
  by comparing the two methods.
| The libraries *pylsd-nova* :cite:`ipol.2012.gjmr-lsd` and
  *opencv-fld* :cite:`fld` are python implementation of the
  two selected methods. They both have a number of parameters that allow
  adjusting line segment detection according to the user’s needs. To
  compare them, we chose the default settings. However after several
  executions we realized that we needed to add our own parameters to
  better guide the algorithm according to our specific requirements,
  they are listed in Table 3.

.. figure:: /_static/orcult/IMGS/table3.png
   :alt:
   :width: 70.0%
   :align: center

| Firstly, we noticed that at the edge of the plot, there could be a
  certain number of irrelevant segments that are not coherent with the
  overall orientation of the plot and that needed to be removed from the
  calculation [Figure 7b]. One probable cause of these
  misaligned peripheral segments is the particular work of agricultural
  machinery at the headland. They can also result from poor definition
  of the plot’s geometry. A parameter of erosion has therefore been
  introduced to suppress peripheral segments. A value of 5m is
  appropriate for the area studied [Figure 7c]. Next, we
  chose to only keep segments that are longer than 6 meters. Indeed,
  some segments shorter than this length are generally not associated
  with rows, since a significant percentage of them did not follow the
  overall direction of the plot [Figure 7d]. Finally, in
  order to minimize errors, we set a minimum threshold for the number of
  segments within a plot. The fewer segments there are within the plot,
  the less reliable the orientation calculation is. We set this
  threshold to 10.
| If the plot did not meet all of these criteria, the orientation is not
  calculated.

Orientation computation
~~~~~~~~~~~~~~~~~~~~~~~

Once the segment selection is done within each plot, we calculate the
median vector :math:`(x_{med}, y_{med})` that is representative of the
segments distribution according to the equation, which
allows us to determine the overall direction of the crop. :math:`S`
represents the set of all segments selected within a plot.

.. math::

   x_{med} = \underset{\overrightarrow{AB} \in S}{\mathrm{median}} (\frac{x_B - x_A}{| \overrightarrow{AB} |}) \quad\text{and}\quad y_{med} = \underset{\overrightarrow{AB} \in S}{\mathrm{median}} (\frac{y_B - y_A}{| \overrightarrow{AB} |})
       \label{eq1}

To visualize this information effectively, we pass it through the
centroid of the plot :math:`(x_c, y_c)` and extend it to the edges
[Figure 7e & 7f]. The Figure 7
illustrates this process where the overall orientation of the plot is
represented in black.

.. figure:: /_static/orcult/IMGS/process.png
   :alt:
   :width: 60.0%
   :align: center


As stated in paragraph 2.2.3, it is possible that several
plots are grouped together in the same vector geometry. We noticed that
if we did not distinguish simple from complex parcels, we would have a
discrepancy between the global orientation of the parcel and the
distribution of the segments belonging to it. This is what we observe in
the Figure 8, the histograms correspond to
the distribution of the segments when we compare them to the global
orientation calculated by the algorithm. In a simple case like the field
visible on the left of the figure, the result is straightforward. On the
other hand, for the other plot, 2 groups of segments with almost
orthogonal orientations are noticed. It is therefore necessary to first
separate the cases where the plot has only one orientation from the ones
where it has multiple.

.. figure:: /_static/orcult/IMGS/multiorient_clusters.png
   :alt:
   :width: 60.0%
   :align: center

Multi-orientation detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To address the aforementioned issue, we have considered using a
clustering-based segmentation method. Among them, the mean shift
algorithm :cite:`meanshift` is a wise way to approach the
problem because we do not clearly know how many line clusters to
identify.

Initially, we implemented a method that only considered the direction of
each segment. This would work nicely for the multi-plot case illustrated
in Figure 8. Indeed, the clustering method
allows us to identify two distinct clusters: the red segments and the
yellow segments as their direction are very different and easy to
separate. It is then simple to deduce two distinct orientations for the
same plot, one for the sub-plot containing the red segments and one for
the one containing the yellow segments. However, this approach exposed
problems for extreme cases like the plot shown in
Figure 9 where certain subplots, located far apart,
have segments with similar directions. Therefore, we had to introduce
the segment’s position, approximated by its center, as an input to our
clustering model. After data normalisation, one must remain alert in the
fine tuning of mean-shift and always allow more importance to the angle
than to the position, four times more in our case after several tests
[Table 3]. Without this setting, too many clusters
may appear, artificially creating plots that in fact are not.

There are two possible scenarios after the mean-shift algorithm. If the
number of identified clusters is equal to 1, then the plot does not have
multiple orientations, and the previously calculated overall orientation
is retained. If the number of clusters is greater than 1, we only keep
the significant clusters, which are composed of a minimum of 10
segments, as described in Table 3. Once these
clusters are identified, as shown in blue, purple and white in left
image of Figure 9, new plots are created from the
convex hulls of each cluster, dilated until reaching the extent of the
original parcel. This is what we observe on the right image of
Figure 9, the original plot was further refined into
3 distinct geometries through the orientation detection algorithm.

.. figure:: /_static/orcult/IMGS/bad_example.png
   :alt:
   :width: 70.0%
   :align: center

Code parallelization
--------------------

To save computation time and avoid overloading the processes, it is
possible and highly recommended to divide the input images into smaller
patches and assign them to separate processes, thus performing the
computations synchronously. Naturally, this technique requires treating
the plots at the edges of the patches and the plots fully included
within the pacthes separately. By way of illustration, the typical
processing time for one French department is a few hours for our python
implementation on our hardware, depending on the number of plots
processed, their complexity and the method implemented. For each
department we used 24 CPU cores and 120 GB of RAM.

.. figure:: /_static/orcult/IMGS/table4.png
   :alt:
   :width: 70.0%
   :align: center

Results
=======

In this section we will provide information about the performances of
our algorithm, depending on location and crop type, its accuracy and
discuss about its strengths and limitations.

Overview
--------

In order to have the safest possible method of orientation detection, a
series of tests was conducted across multiple departments in the French
territory visible in Table `[detection] <#detection>`__. Each of them
being different in terms of cultural composition, terrain quality, and
climatic conditions. First, we examined the amount of data that the
algorithm could provide, namely the probability of finding an
orientations, while carefully observing potential differences in
performance based on culture type, geographic location, and the date of
the aerial imagery from the BD ORTHO database. Then, using the ground
truth established in 2.2.5, the effectiveness and accuracy
of the algorithm has been analysed, while studying the limitations of
our approach.

Orientation detection probability
---------------------------------

.. figure:: /_static/orcult/IMGS/table5.png
   :alt:
   :width: 70.0%
   :align: center

Table 5 gathers information about orientation
detection using both segment detection methods. A trend seems to emerge
across all departments in the study. At default settings, the
*opencv-fld* library appears to detect more segments within the images,
resulting in a higher percentage of detected plots with an orientation.
Consequently, it also detects more multi-oriented plots.

In addition, the orientation detection probability can vary greatly from
one region to another. Multiple factors can influence this outcome.
Firstly, the cultural composition of the department plays a significant
role. For instance, certain types of crops, such as vineyards are
cultivated in formatted rows as shown in Figure 10.
The orientation of this crop type is among the easiest to detect. Any
department with a large fraction of vines will therefore have a higher
probability of orientation detection as illustrated in
Figure 11 and
Table 6.

.. figure:: /_static/orcult/IMGS/vine_and_corn.png
   :alt:
   :width: 80.0%
   :align: center

In the case of the Gers department, the algorithm is more comfortable
detecting the orientation of vineyards rather than that of corn or any
other crop in general. On the other hand, if we take a closer look to
wheat crops, we clearly see big changes from a region to another. The
departments like Gers, Jura, or Haute-Saône have very high detection
rates for this crop, exceeding 90%. Whereas for Côte-d’Or, the
percentage is much lower, close to 40%. This significant difference
steers us to study a second influencing factor : the acquisition date of
the input images.

.. figure:: /_static/orcult/IMGS/fig1.png
   :alt: 
   :width: 70.0%
   :align: center

.. figure:: /_static/orcult/IMGS/fig6.png
   :alt:
   :width: 60.0%
   :align: center

When discussing image information extraction for agriculture, it is
essential to consider the acquisition date. Crops evolve rapidly over
time, especially during periods of high growth. Even a short time delay
in capturing the image can have varying consequences on the obtained
results :cite:`rs11182143`. Moreover, in our BD ORTHO
dataset, the acquisitions dates can be spaced several weeks apart
[:ref:`appendix-a`]. As an illustration, between Gers and Côte-d’Or,
we noticed that the acquisition dates are completely different, June for
one and September for the other. This is crucial information, especially
when considering that the harvest period for wheat during July and
August :cite:`recolte` . This explains the low percentage of
wheat orientation detection in the Côte-d’Or department because, simply
put, most of the wheat crops have already been harvested. Wheat fields
were empty or dethatched as visible in Figure 12, making
orientation detection much more difficult.

.. figure:: /_static/orcult/IMGS/wheats.png
   :alt:
   :width: 70.0%
   :align: center

A closer look at the date dependency of wheat results in Figure
13 reveals a clear decline in algorithm performance
between May and September. This date dependence of the orientation
detection probability is certainly true for all seasonal crops, but with
different properties from one crop to another.

.. figure:: /_static/orcult/IMGS/fig4.png
   :alt: 
   :width: 70.0%
   :align: center

Orientation angle accuracy
~~~~~~~~~~~~~~~~~~~~~~~~~~

Having studied the probability of detecting an orientation, let us now
try to define its quality. The metric used is simple: we compare the
orientation calculated by the algorithm to our ground truth, by
calculating the angle described by the two segments red and yellow in
Figure 14.

.. figure:: /_static/orcult/IMGS/precision_figure.png
   :alt:
   :width: 70.0%
   :align: center

Since the expected accuracy of the orientation angle could vary from one
application to another, the success rate has been computed with
different thresholds as visible in
Table 7. Overall, our method
detects the orientation angle to better than 5° about 93% of the times
with the *opencv-fld* implementation of LSD.

.. figure:: /_static/orcult/IMGS/table7.png
   :alt:
   :width: 70.0%
   :align: center

Then, we noticed that the algorithm performance varies significantly
when going from a threshold of 1° to 2°. This can be explained by the
precision of our ground truth pointing, as reported in section
 2.2.5. Generally speaking, the performances are very
similar between the two LSD implementation, with a slight advantage for
the *pylsd-nova* one. This is however balanced by a higher percentage of
detection of multi-oriented plots with *opencv-fld*
[Table 5], which at times can detect more
orientations within a plot than what we had determined when creating the
ground truth. Consequently, this increases the risk of inaccuracy. This
is confirmed for the Ille-et-Vilaine department, where the *opencv-fld*
method appears to be more accurate, a region where multi-oriented plots
are less common than elsewhere [Table 5].

Effect of spatial resolution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The difference in spatial resolution between Pléiades and BD ORTHO
images is significant. There is a pixel sizes ratio of 2.5 between the
two image types. Pléiades images have a pixel size of 50 cm and a native
ground sampling distance of 70cm while of the BD ORTHO pixel size is 20
cm. With a very distant view, it is difficult to see the difference with
the naked eye. This difference becomes apparent when applying an
exaggerated zoom, as illustrated in Figure 15. It is
interesting to check if this difference can have an impact on the
algorithm’s behavior and potentially evaluate its importance. For this,
we used a subset of 3,151 vineyard plots in the Aude department. We
applied our algorithm and compared the output numbers. Among them, we
recorded the number of detected segments in the subset of plots, the
associated number of orientations, and the accuracy of these
orientations [Table 8]. The accuracy is
computed as the standard deviation of the difference between the
orientation angle and our ground truth, made up of 50 plots of vines in
this department.

.. figure:: /_static/orcult/IMGS/diff_bdortho_pleiades.png
   :alt: 
   :width: 60.0%
   :align: center

.. figure:: /_static/orcult/IMGS/table8.png
   :alt:
   :width: 60.0%
   :align: center

It can be observed that a much larger number of segments is detected
with BD ORTHO images, and in addition to that, these segments are longer
and with directions that are more consistent. Figure 16
illustrates the consequences of the difference in resolution on the
quality of segment detection.

.. figure:: /_static/orcult/IMGS/kep_lines.png
   :alt:
   :width: 60.0%
   :align: center

This visual perception that we observe is confirmed when focusing on a
specific plot while plotting the distribution of segments orientation
[Figure 17]. In the case of the BD ORTHO
dataset, the distribution is highly concentrated around the main
orientation, whereas in the Pléiades dataset, it is much more spread
out. Consequently, the precision in calculating median orientation is
directly affected, this is illustrated in Table 8.

.. figure:: /_static/orcult/IMGS/distributions.png
   :alt: 
   :width: 70.0%
   :align: center

Discussion
==========

Throughout the presentation of the method and its results, we have
described various limitations such as the quality of the remote sensing
input image, the date of acquisition, the type of culture. But, there
are also limitations coming from specific image contents.

After the segments detection step, we filter them according to their
length and location but sometimes this is not enough to distinguish that
they are not linked to the rows. Indeed, by visual inspection, we could
observe that, in some cases, the detected segments were linked to
tractor tracks. Fortunately, the tractor tracks are generally aligned
with the rows. By looking for cases in which there is a very large
difference between the ground truth and the output of our algorithm, we
have also identified cases where a path crosses the rows diagonally.
Here, if the plot has few visible rows, our algorithm will be misled.
Our method can also be affected by human installations with linear
geometries, such as high-voltage power lines [Figure 18].

Despite the different filtering steps performed to prevent irrelevant
segments from having a negative influence on the final orientation of
the plot, there will always be cases where segments pass the filter and
finish being responsible for an inaccurate or wrong final orientation.
Some segments may be assigned to their own cluster in the
multi-orientation detection step, wrongly suggesting the presence of a
sub-plot. Finally, highly disorganised crops are rarely observed, in
which the orientation, even visually, can’t be unambiguously identified.

.. figure:: /_static/orcult/IMGS/haute_tension3.png
   :alt: 
   :width: 60.0%
   :align: center


The performance of our algorithm can be summarized by two metrics : the
probability of finding an orientation in a given plot and, in case of
success, the orientation accuracy. Those 2 metrics have been evaluated
on 8 different crops spread over more than 300,000 plots in France : the
orientation detection probability is 63 % and the orientation accuracy
is 93% with a 5° threshold and 81% with a 2° threshold. These metrics
are valid for a single trial based on a 20cm BD ORTHO image. So it’s
easy to find more plot orientations by multiplying orientation detection
tests from several images in the same area. In doing so, it appears
realistic to obtain on a very large scale, and with a very good level of
precision, the orientation of most cultivated fields. We believe that
this work paves the way for the development of applications using crop
orientation.

We observe a clear dependence of the performance of our method on the
crop type. On our dataset, while the probability of finding at least one
orientation for a given plot is 67% for vines or wheat, it drops to 24 %
for orchard. All BD ORTHO images were taken between may and september,
simply because it maximizes solar illumination while limiting cloud
cover. So the orientation detection probability dependence on crop type
is therefore certainly biased by the limited temporal range of our image
set, most of which was acquired in summer. Indeed, by studying the
dependence of our results on the date of acquisition, we observe that
the probability of finding at least one orientation for a plot of wheat
falls from over 90% in May to about 30% in September. This indicates,
unsurprisingly, that the probability of finding an orientation depends
on growth status and farming practices. In fact, hardly any fields are
in a ploughed state, even though this condition that is generally met in
autumn and winter could give good results too.

Pixel size has a critical impact on the general performance of our
method too. Moving from Pléiades to BD ORTHO, with respective pixel of
50cm to 20cm, significantly increase the number of detected segments
inside the plots. This has a direct impact on the probability of finding
an orientation, as well as on the orientation accuracy. The tests we
have carried out on vines show that, when an orientation is found, its
accuracy drops from more than 10 degrees with Pleiades to less than 1
degree with BD ORTHO.

Generally speaking, the main external limitation of our method is the
visible presence in the input image of rows or traces of agricultural
machinery. The errors potentially induced by bad segments in the
periphery of the plots, particularly in the U-turn zones, are generally
well managed by our erosion parameter. This parameter will have to be
adapted if our tool is used in territories with plot sizes or tractor
sizes that are significantly different from those encountered in France.
The accuracy on the orientation angle is mainly limited by two external
factors : terrain effect that makes row not straight in the images after
orthorectification, but also non-rectilinear row generally found in
atypically shaped plots. Cases of indisputable failure occur in very
specific and rare conditions. We have identified a few cases in our
entire dataset that are linked to high voltage lines or straight paths
crossing plots where the orientation is moreover hardly visible. It is
not possible to give a probability of occurrence for these cases, as we
have not observed them often enough. However, we believe that the
maximum limit is around 1/1000.

Except in the case of reparcelling, crop orientation is fairly static
from one year to the next. To create a very large-scale database, it
would be therefore possible to build it iteratively, by using every
available image, whatever its date or resolution. GPR was used as it
provides a solid basis for defining plots with a combined crop. However,
we noted that 16 % of the plots as defined in the GPR are in fact
multiple plots. Moreover, its coverage is limited to Europe, this would
make the production of a global crop orientation product impossible.
With a view to mass production, we suggest using endogenous plot
geometry detection. Although this is not the subject of our work here,
we can even anticipate that it will be useful to refine this processing
step thanks to our multi-oriented plot detection.

**funding :** This research received no external funding

**Data availability statement :** The data presented in this study are available at the following `URL <https://doi.org/10.5281/zenodo.8316341>`_

**Conflicts of interest :** The authors declare no conflict of interest.


Abbreviations
-------------

The following abbreviations are used in this manuscript:

**ADS**         Airbus Defence and Space

**BAR**         Barley

**BD ORTHO**    French ortho-image database

**BRDF**        Bidirectional reflectance distribution function

**CNES**        Centre National d'Etudes Spatiales

**COR**         Corn

**DPT**         Department

**GPR**         Graphical Parcel register

**IGN**         Institut National de l'information géographique et forestière

**LSD**         Line Segment Detector

**NIR**         Near Infrared

**OCE**         Other cereal

**ORC**         Orchard

**SFL**         Sunflower

**SWIR**        Short Wave Infrared

**VFL**         Vegetables/Flowers

**VIN**         Vine

**WHT**         Wheat

.. _appendix-a:

Appendix A
----------

.. figure:: /_static/orcult/IMGS/appendix.png
   :alt:
   :width: 60.0%
   :align: center

.. [1]
   Public administrative institution whose mission is to ensure the
   production, maintenance and dissemination of referenced geographic
   information in France

.. [2]
   available here : https://geoservices.ign.fr/bdortho

Bibliography
~~~~~~~~~~~~

.. bibliography:: ref.bib
   :style: plain

