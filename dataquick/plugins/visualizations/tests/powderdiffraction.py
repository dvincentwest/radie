import sys

from PyQt5 import QtWidgets

from dataquick.plugins import examples
from dataquick.qt import functions as fn
from dataquick.qt.masterdqftree import DQFReference
from dataquick.plugins.visualizations.powderdiffraction import VisPowderDiffraction

app = QtWidgets.QApplication(sys.argv)

fn.set_popup_exceptions()

form = VisPowderDiffraction()
df = examples.example_powderdiffraction()
ref = DQFReference(df, None)
form.listView_datasets.addDataFrames(*[ref, ref, ref])
form.show()
sys.exit(app.exec_())
