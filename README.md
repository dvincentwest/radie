![image](radie/qt/resources/icons/radie.svg)


# Rapid Data Import Environment (radie)

Copyright (&copy;) 3M Company, 2018, 

License: GPL version 2 

Radie is a python package for experimental data primarily using pandas
for data structures

The point of radie is to remove the pain of loading and visualizing
experimental data. It is not meant for complex plotting or pretty
pictures, but rather a focus on rapidly converging experimental data
stored in files into a single place for rapid visualization.

## Python Usage

```python
import radie as rd
df = rd.DataStructure(data=[1, 2, 3], name="data frame")
print(df.metadata["name"])
print(df.metadata["date"])

csv_df = rd.load_file("my_random_data.csv")  # unspecified csv data

pow_df = rd.load_file("powder_diffraction_measurement.ras")  # powder diffraction data
print(pow_df.metadata["name"])

vsm_df = rd.load_file("magnetization_v_field.txt")  # VSM measurement
print(vsm_df.metadata["name"])
```

## Launch PyQt Gui

```shell
python -m radie.qt.viewer
```

## Requirements
- numpy
- pandas

additionally for the gui application:
- pyqt >= 5.6
- pyqtgraph >= 0.10

## Installation

    pip install radie
    
or for the latest updates, clone this repo and add radie/ to your PythonPath

On Windows, running the `install_windows_shortcut.py` script will install
shorcuts for radie using the same python executables that are used to
run the install script.

## Highlights

-   Core Features:
    -   DataStructure - base class, just a pandas DataFrame with some
        restrictions, metadata and templates for more specific
        sub-classes
    -   CSV importer that under some structure assumptions attempts to:
        -   automatically determine delimiter
        -   automatically find the csv data-block
        -   automatically determine headers
        -   ignore preceding metadata
    -   Qt-based Gui Viewer with Drag and Drop handling of files and
        data-set comparison
-   Extensible because (nearly) everything is a plugin
    -   DataStructure subclasses specify structured data
        (add-your-own!)
    -   Custom Visualizations of Structured Data, based on whatever fits
        into QMdiSubwindow (I use PyQtGraph)
    -   File-loaders written for each supported file-type, register into
        the system so that radie.load\_file can automatically detect
        and load registered file-types
    -   \*\*GUI save files keep all your rapid analysis in one place
        each plugin specifies its own save data in json format and all
        DataStructures have a common save format

\*\* Planned, but not yet implemented

## Currently Supported File-types

-   PowderDiffraction:
    -   Rigaku (.asc, .ras)
    -   Bruker (.raw (v2))
    -   GSAS (.raw, .gsas, .fxye)
-   VSM:
    -   Lakeshore (.dat, .txt (Field v Moment))

## Vision

Radie is not a replacement for Origin, Igor, QtiPlot or similar gui
scientific plotting/analysis packages. Instead Radie has the
following goals:

1.  import data files, with drag and drop and automatic file-type
    detection
    -   powder diffraction data
    -   spectrum data
    -   any data that maps to a Pandas DataStructure
2.  rapid comparison of datasets into automatically generated
    visualizations with drag and drop
    -   I don't want to plot things, I want to visualize them, the
        software should plot for me
3.  reasonable interoperability with python for more complex operations
    -   matplotlib, bokeh, whatever, I want to do the quick
        visualizations and comparisons in a gui, and I will do all of
        the complicated analysis and crazy figure plotting in something
        more flexible like a Jupyter Notebook
    -   strong clipboard integration
    -   common file-saving scheme for all types of data
4.  saving my collected datasets and visualizations
    -   Origin/QtiPlot software is not my cup of tea for actually
        analyzing data but its nice to save your collection of data and
        plots in a single spot
    -   Jupyter Notebooks / Matplotlib are much nicer when it comes to
        analyzing data but all of that flexibility can screw things up
        in the future, it would be nice to have it all in one
        re-producible place that I can come back to at any time with a
        double click of the mouse
5.  reasonable exporting to excel
    -   Excel is the most wide-spread format for sharing/visualizing 1-D
        datasets and these datasets are literally everywhere. A quick
        button to make an excel file to share with the non-programmers
        out there is critical
