import dataquick as dq
import pathlib
import os

this_dir = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))
data_file = this_dir / "../dataquick/plugins/examples/data/barium_ferrite.ras"
data_file = this_dir / "../dataquick/plugins/examples/data/idea_vsm.txt"

df = dq.load_file(data_file)
print(df.head())

# df.savetxt()