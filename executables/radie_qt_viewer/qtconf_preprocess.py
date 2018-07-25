"""account for Anaconda specific packaging of PyQt which is different than the pip wheel"""

import sys
from pathlib import Path
import os

dll_path = Path(sys.exec_prefix)
qtconf = dll_path / 'qt.conf'

if qtconf.exists():
    with open(qtconf) as fid:
        for line in fid:
            if line.startswith('Prefix'):
               prefix = Path(line.split('=')[1].strip())
               plugin_path = prefix / 'plugins'
               if plugin_path.exists():
                   os.environ['QT_PLUGIN_PATH'] = str(plugin_path)
                   break
