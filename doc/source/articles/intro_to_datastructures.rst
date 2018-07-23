Introduction to Data Structures
===============================

Data structures get at the heart of what radie is for.  Many kinds of data
can easily be represented as labeled columns of data, combined with meta-data.
The pandas python module provides a robust framework for this in the form of a
DataStructure.  For this module we define a lightly modified DataStructure subclass
called a :doc:`DataStructure</api/dataframe>`

As a DataStructure is a pandas dataframe, you can manipulate it in all the same
ways that you can manipulate a DataStructure. The essential distinguishing attributes
of a DataStructure are (Please see the API page for further details):

* `_required_columns` , a class attribute defining data that a particular
  structure must have.  For example, a powder diffraction measurement must have
  two columns: scattering angle (twotheta) and scattering intensity (intensity).
* `_required_metadata` , a class attribute defining which values are required
  to completely determine the dataset.  For example, a powder diffraction
  measurement must specify the wavelength of the incident radiation, which is
  1.5414 for Cu-K\u0251, but may be different for Synchrotron X-Ray or Neutron
  Powder diffraction measurements.

In the base class these attributes have empty values,
meaning that in structure, the base class is no different than a pandas
dataframe.  Rather the structure is meant to be specified in subclasses

By specifying the structures, it allows us to label and organize data sets, and
more rapidly group them, and compare them, and visualize them in complex ways
under the assumptions of their structures.  In short, in the environment of many
different types of datasets provided from measurements from many different
vendors, it can greatly speed up analysis when dealing with many datasets.
