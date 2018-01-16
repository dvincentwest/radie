What is DataQuick
=================

.. toctree::

DataQuick is a python package whose purpose is to make it easy for scientists
(or anybody) to rapidly import, export, visualize and compare scientific
datasets.

An Example
----------
I'm working on a materials development project.  Today, I just got my results
back from particle size analysis.  I have five samples.  Let me open my gui
software, and through drag and drop all the files are imported and populated as
individual items in a list.  I want to look at them all on the same plot.  I
open a new visualization for PSD files and drag and drop the datasets onto it,
and the datasets appear in the plot.  The datasets represent a monotonic change
in synthesis conditions, say 1-5, but the items are out of order.  No problem, I
click and drag to reorder them in the list of the plot.  It all takes maybe 30
seconds.  

Next I want to compare these data to the X-ray diffraction peak widths for the
same materials.  I measured those last week and have the binary save files in
the Bruker .raw format.  As before, I drag the files onto the GUI application.
I open a Visualization for powder diffraction and drag the datasets onto and
they populate the plot as before.  I rearrange the datasets as necessary.
Again, it takes about 30 seconds.

In More Detail
--------------
In the course of scientific research, either at the instrument, back at the
desk, or somewhere in a meeting, the scientist will often have a few sets of
data that he or she wants to look at, rapidly, and comparing the datasets to
eachother.  Today, that means working with dedicated software for the specific
measurement type, or importing the data into Excel, Matlab, Origin, Python, or
some other software.  In the case of dedicated software, it might be expensive,
or not widely available.  Or it might be poorly written with very few options
and bad export features.  The general analysis software packages meanwhile,
typically have remarkable flexibility.  However, the process of importing and
making comparison plots can often be quite cumbersome and tedious.

DataQuick is meant to fill this gap in speed, providing a framework for very
rapid import and visualization of datafiles.  To make it work, each class of
scientific data must have a defined structure (see DataQuickFrame).  Then, for
each specific file-type containing a measurement, there must be a defined
function that loads the datafile into the defined structure.  Furthermore, the
loader functions are associated with file-extensions, and behave in such a way
that they can all be collected, and the underlying system can automatically
determine the correct loader function to use for the given datafile (see Loader)
Lastly, there must be a defined visualization which provides appropriate display
and interaction with the data (see Visualization).

Although it is possible to use dataquick in an interactive coding environment
such as Jupyter or Spyder, its original motivation was to create a GUI
application.  This application is the DataQuick Viewer, written in PyQt.  It is
currently a work in progress, but already provides the basic functionality to
import data files, visualize them in interactive plot widgets, and quickly
compare data sets to one another in generic or application specific
visualizations.

Extending through Plugins
-------------------------
New datastructures, data file types and visualizations can be added by writing
plugins.  Over time, the goal is for DataQuick to grow supporting many different
data sets and file types through contributed plugins.  See `writing plugins` and
`contributing` for more information.

Fast and Easy to Use, Not to Extend
-----------------------------------
It should be noted that the point of the general analysis software listed above
is to make it easy to import data and create complex plots.  However, because it
is easy, it is slow.  DataQuick takes the opposite approach.  It can be a lot of
work to define a structure, write one or more loader functions for files of that
structure and then create a complex visualization.  For a one-time use you would
never do this.  However, by putting the work in at the beginning to create these
tools, you reuse it over and over, and the process of data analysis becomes much
more rapid and much more satisfying without the tedium of plotting from scratch.

Easier than starting from scratch
---------------------------------
Although it is not *easy* to write plugins, it is not substantially more
difficult than other kinds of python programming. And because the plugins can
plugin to the infrastructure already provided, the contributer can take
advantage of some of the 
