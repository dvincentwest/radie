"""convenience testing package to generate example DataFrames from example data"""
import os

from ..loaders import vsm_lakeshore, powderdiffraction_rigaku

this_dir = os.path.dirname(__file__)


def example_powderdiffraction():
    """
    return an example `PowderDiffraction` generated by an example data file

    Returns
    -------
    df : PowderDiffraction

    """
    example_ras_file = os.path.join(this_dir, "data/barium_ferrite.ras")
    df = powderdiffraction_rigaku.load_ras(example_ras_file)
    return df


def example_vsm():
    """
    return an example `VSM` generated by an example data file

    Returns
    -------
    df : VSM

    """
    example_file = os.path.join(this_dir, "data/idea_vsm.txt")
    df = vsm_lakeshore.load_ideavsm_txt(example_file)
    return df