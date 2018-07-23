import radie as rd
import pathlib
import os

this_dir = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))
data_file = this_dir / "../radie/plugins/examples/data/barium_ferrite.ras"
data_file = this_dir / "../radie/plugins/examples/data/idea_vsm.txt"

df = rd.load_file(data_file)
print(df.head())

# df.savetxt()