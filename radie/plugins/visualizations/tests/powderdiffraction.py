import sys

from PyQt5 import QtWidgets

from radie.plugins import examples
from radie.qt import functions as fn
from radie.qt.masterdftree import DFReference
from radie.plugins.visualizations.powderdiffraction import VisPowderDiffraction

app = QtWidgets.QApplication(sys.argv)

fn.set_popup_exceptions()

form = VisPowderDiffraction()
df = examples.example_powderdiffraction()
ref = DFReference(df, None)
form.listView_datasets.addDataFrames(*[ref, ref, ref])
form.show()
sys.exit(app.exec_())
