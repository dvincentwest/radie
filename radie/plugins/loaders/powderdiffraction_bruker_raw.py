import struct
import numpy as np
from datetime import datetime

from radie import exceptions
from radie.loaders import Loader, register_loaders
from radie.plugins.structures.powderdiffraction import PowderDiffraction


def raw_check_version(f):
    """

    Parameters
    ----------
    f : file object

    Returns
    -------
    version : string or None
    """
    f.seek(0)
    head = read_str(f, 4)
    version = None

    if head == "RAW ":
        version = "ver. 1"
    elif head == "RAW2":
        version = "ver. 2"
    elif head == "RAW1" and read_str(f, 3) == ".01":
        version = "ver. 3"

    return version


def load_raw(fname, name=None):
    """
    .raw file output from Bruker XRD.  Tested with files from Bruker D8
    Ported from xylib\bruker_raw.cpp

    If multiple ranges exist in the RAW file a list of PowderDiffraction StructuredDataFrame
    objects are returned. If only one a single object is returned

    Parameters
    ----------
    fname : str
        filename
    name : str
        measurement identifier

    Returns
    -------
    df_xrd : single PowderDiffraction or list of them
        PowderDiffraction StructuredDataFrame based on XRD data

    """

    with open(fname, 'rb') as f:
        version = raw_check_version(f)
        if version == 'ver. 3':
            dfs = load_raw_version1_01(f, name=name)
        else:
            raise exceptions.IncorrectFileType

    if isinstance(dfs, PowderDiffraction) or type(dfs) in (list, tuple):
        if len(dfs) == 0:
            raise IOError('Unable to read scan from file')
        elif len(dfs) == 1:
            return dfs[0]
        else:
            return dfs
    else:
        raise TypeError("Unrecognized StructuredDataFrame type: {:}".format(type(dfs)))


def read_int(f):
    return struct.unpack('<i', f.read(4))[0]


def read_dbl(f):
    return struct.unpack('<d', f.read(8))[0]


def read_flt(f):
    return struct.unpack('<f', f.read(4))[0]


def read_str(f, len):
    return f.read(len).decode('utf-8').rstrip('\x00')


def load_raw_version1_01(f, name=None):
    """
    Read a file object pointing to a Bruker RAW file of version 1.01
    Since RAW files can contain more than one scan (or range) a
    list of PowderDiffraction dataframes are returned

    Parameters
    ----------
    f : file object

    Returns
    -------
    dfs : list of PowderDiffraction objects
    """
    meta = {}
    meta["format version"] = "3"

    f.seek(8)  # jump to after version line
    file_status = read_int(f)  # address 8

    if file_status == 1:
        meta["file status"] = "done"
    elif file_status == 2:
        meta["file status"] = "active"
    elif file_status == 3:
        meta["file status"] = "aborted"
    elif file_status == 4:
        meta["file status"] = "interrupted"

    range_cnt = read_int(f)  # address 12

    meta["MEASURE_DATE"] = read_str(f, 10)  # address 16
    meta["MEASURE_TIME"] = read_str(f, 10)  # address 26
    meta["USER"] = read_str(f, 72)  # address 36
    meta["SITE"] = read_str(f, 218)  # address 108
    meta["SAMPLE_ID"] = read_str(f, 60)  # address 326
    meta["COMMENT"] = read_str(f, 160)  # address 386
    f.read(2)  # apparently there is a bug in docs, 386+160 != 548
    f.read(4)  # goniometer code # address 548
    f.read(4)  # goniometer stage code # address 552
    f.read(4)  # sample loader code # address 556
    f.read(4)  # goniometer controller code # address 560
    f.read(4)  # (R4) goniometer radius # address 564
    f.read(4)  # (R4) fixed divergence...# address 568
    f.read(4)  # (R4) fixed sample slit...# address 572
    f.read(4)  # primary Soller slit # address 576
    f.read(4)  # primary monochromator # address 580
    f.read(4)  # (R4) fixed antiscatter...# address 584
    f.read(4)  # (R4) fixed detector slit...# address 588
    f.read(4)  # secondary Soller slit # address 592
    f.read(4)  # fixed thin film attachment # address 596
    f.read(4)  # beta filter # address 600
    f.read(4)  # secondary monochromator # address 604
    meta["ANODE_MATERIAL"] = read_str(f, 4)  # address 608
    f.read(4)  # unused # address 612
    meta["ALPHA_AVERAGE"] = read_dbl(f)  # address 616
    meta["ALPHA1"] = read_dbl(f)  # address 624
    meta["ALPHA2"] = read_dbl(f)  # address 632
    meta["BETA"] = read_dbl(f)  # address 640
    meta["ALPHA_RATIO"] = read_dbl(f)  # address 648
    f.read(4)  # (C4) unit name # address 656
    f.read(4)  # (R4) intensity beta:a1 # address 660
    meta["measurement time"] = read_flt(f)  # address 664
    f.read(43)  # unused # address 668
    f.read(1)  # hardware dependency... # address 711
    # assert (f.tellg() == 712);

    # Expected meta
    # Convert to datetime
    timestamp = datetime.strptime('{} {}'.format(meta["MEASURE_DATE"], meta["MEASURE_TIME"]), '%m/%d/%y %H:%M:%S')
    meta['date'] = timestamp.isoformat()

    # range header
    dfs = []
    for cur_range in range(range_cnt):

        if name is None:
            meta["name"] = '{}-{}'.format(meta["SAMPLE_ID"], cur_range)
        else:
            meta["name"] = '{}-{}'.format(name, cur_range)

        # Take off the number of only one
        if range_cnt == 1:
            meta["name"] = meta["name"][:-2]

        # Block * blk = new Block;
        header_len = read_int(f)  # address 0
        assert header_len == 304

        steps = read_int(f)  # address 4
        meta["STEPS"] = steps
        start_theta = read_dbl(f)  # address 8
        meta["START_THETA"] = start_theta
        start_2theta = read_dbl(f)  # address 16
        meta["START_2THETA"] = start_2theta

        f.read(8)  # Chi drive start # address 24
        f.read(8)  # Phi drive start # address 32
        f.read(8)  # x drive start # address 40
        f.read(8)  # y drive start # address 48
        f.read(8)  # z drive start # address 56
        f.read(8)  # address 64
        f.read(6)  # address 72
        f.read(2)  # unused # address 78
        f.read(8)  # (R8) variable antiscat.# address 80
        f.read(6)  # address 88
        f.read(2)  # unused # address 94
        f.read(4)  # detector code # address 96
        meta["HIGH_VOLTAGE"] = read_flt(f)  # address 100
        meta["AMPLIFIER_GAIN"] = read_flt(f)  # 104
        meta["DISCRIMINATOR_1_LOWER_LEVEL"] = read_flt(f)  # 108
        f.read(4)  # address 112
        f.read(4)  # address 116
        f.read(8)  # address 120
        f.read(4)  # address 128
        f.read(4)  # address 132
        f.read(5)  # address 136
        f.read(3)  # unused # address 141
        f.read(8)  # address 144
        f.read(8)  # address 152
        f.read(8)  # address 160
        f.read(4)  # address 168
        f.read(4)  # unused # address 172
        step_size = read_dbl(f)  # address 176
        meta["STEP_SIZE"] = step_size
        f.read(8)  # address 184
        meta["TIME_PER_STEP"] = read_flt(f)  # 192
        f.read(4)  # address 196
        f.read(4)  # address 200
        f.read(4)  # address 204
        meta["ROTATION_SPEED [rpm]"] = read_flt(f)  # 208
        f.read(4)  # address 212
        f.read(4)  # address 216
        f.read(4)  # address 220
        meta["GENERATOR_VOLTAGE"] = read_int(f)  # 224
        meta["GENERATOR_CURRENT"] = read_int(f)  # 228
        f.read(4)  # address 232
        f.read(4)  # unused # address 236
        meta["USED_LAMBDA"] = read_dbl(f)  # 240
        f.read(4)  # address 248
        f.read(4)  # address 252
        supplementary_headers_size = read_int(f)  # address 256
        f.read(4)  # address 260
        f.read(4)  # address 264
        f.read(4)  # unused # address 268
        f.read(8)  # address 272
        f.read(24)  # unused # address 280
        # assert (f.tellg() == 712 + (cur_range + 1) * header_len);

        if supplementary_headers_size > 0:
            f.read(supplementary_headers_size)

        # StepColumn * xcol = new StepColumn(start_2theta, step_size);
        # blk->add_column(xcol);
        # VecColumn * ycol = new VecColumn;

        xcol = np.array(range(steps)) * step_size + start_2theta
        ycol = []
        for i in range(steps):
            ycol.append(read_flt(f))
        ycol = np.array(ycol)

        data = np.c_[xcol, ycol]
        df_meta = meta.copy()
        if meta["ANODE_MATERIAL"].startswith('Cu'):
            source = 'CuKa'
        else:
            raise ValueError("Unimplemented Anode Material {}".format(meta["ANODE_MATERIAL"]))
        df_xrd = PowderDiffraction(data=data,
                                   columns=['twotheta', 'intensity'],
                                   wavelength=df_meta['ALPHA_AVERAGE'],
                                   source=source,
                                   xunit="deg",
                                   yunit="counts",
                                   name=df_meta["name"],
                                   date=df_meta["date"],
                                   metadata=df_meta)

        dfs.append(df_xrd)

    return dfs


bruker_raw_loader = Loader(load_raw, PowderDiffraction, [".raw"], "Bruker RAW XRD")

register_loaders(
    bruker_raw_loader,
)
