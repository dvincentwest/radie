import os
import traceback
import sys
import re

import numpy as np
import pandas as pd

from radie import exceptions
from radie.loaders import Loader, register_loaders
from radie.plugins.structures.vsm import VSM


def load_ideavsm_dat(fname):
    """complete experimental output from Lakeshore, missing sample_id information, so we take it from the file"""
    with open(fname, 'r') as fid:
        file_contents = fid.read()  # type: str

    data_line = re.search("\n\*+ Experiment Data \*+\n", file_contents)
    results_line = re.search("\n\*+ Results \*+\n", file_contents)

    if not data_line:
        raise exceptions.IncorrectFileType("Could not locate the DataLine")
    if not results_line:
        raise exceptions.IncorrectFileType("Could not locate the ResultsLine")

    data_string = file_contents[data_line.end():results_line.start()]  # type: str
    data_lines = data_string.splitlines()[1:-1]
    data_length = int(data_lines[0].split(" ")[1].strip())

    data_segments = (len(data_lines) - 1) / (data_length + 1)  # type: float
    if not data_segments.is_integer():
        # data_segments does not appear to be correctly evaluated as a whole number
        raise exceptions.IncorrectFileType

    df = pd.DataFrame()
    for i in range(int(data_segments)):
        start = 1 + i * (data_length + 1)

        data_label = data_lines[start]  # type: str
        if data_label.endswith(" Data"):
            data_label = data_label[:-5]

        data = np.array(data_lines[start + 1: start + 1 + data_length], dtype="float")
        df[data_label] = data
        name = os.path.basename(fname)
    df.rename(columns={"MomentX": "Moment"}, inplace=True)
    return VSM(df, name=name, date=None)


def load_ideavsm_txt(fname):
    """"simple moment v. Field Output from Lakeshore Idea"""

    try:
        with open(fname, "r") as fid:
            header = [fid.readline() for _ in range(12)]
    except EOFError:
        raise exceptions.IncorrectFileType

    #  check to see if this is an understood filetype
    if not (
        header[0].startswith("Start Time: ") and
        header[1].startswith("Sample ID: ") and
        header[3].startswith("Experiment: ") and
        header[4].startswith("Data File: ") and
        header[9].startswith("***DATA***") and
        header[11].startswith("Field(G)\t Moment(emu)")
    ):
        raise exceptions.IncorrectFileType
    name = header[1].strip().split(":")[1].strip()
    date = header[0].strip().split(":")[1].strip().split()[0]

    df = pd.read_csv(fname, sep="\s+", header=8, index_col=False)
    df.rename(columns={"Field(G)": "Field", "Moment(emu)": "Moment"}, inplace=True)
    df_vsm = VSM(data=df, name=name, date=date)
    return df_vsm


lakeshore_ideas_vsm_dat = Loader(load_ideavsm_dat, VSM, [".dat"], "Lakeshore IDEAs VSM (.dat)")
lakeshore_ideas_vsm_txt = Loader(load_ideavsm_txt, VSM, [".txt"], "Lakeshore IDEAs VSM (.txt)")

register_loaders(
    lakeshore_ideas_vsm_dat,
    lakeshore_ideas_vsm_txt,
)
