import re
from datetime import datetime
import time


def excel_sheet_name(name, names_list=[], length=31):
    pattern = "[\\/\*\[\]:\?%&]+"
    clean_name = re.sub(pattern, "", name)[:length]

    if clean_name in names_list:
        base_name = clean_name[:length-3]

        for i in range(100):
            # not going to handle i > 99 errors, because I assume we'll never get that high
            clean_name = base_name + "-{:02d}".format(i)
            if clean_name not in names_list:
                break

    return clean_name


def iso_date_string(dtime=None):
    if type(dtime) in (float, int):
        dtime = datetime(dtime)
    elif not isinstance(dtime, datetime):
        dtime = datetime.now()
    return dtime.isoformat()
