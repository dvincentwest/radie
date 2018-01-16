import dataquick as dq
from dataquick.plugins.loaders import psd_LA960

fname = "C:/Users/A3R7LZZ/Desktop/g12_cgm_170127r4_5j87_avg1.dat"
df = psd_LA960.LA960_csv_loader.load(fname)

df1 = None
