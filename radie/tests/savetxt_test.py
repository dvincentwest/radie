import os
import radie.plugins.examples as ex
df = ex.example_powderdiffraction()
test_file = os.path.join(os.path.expanduser("~"), "Documents/test.df")
df.savetxt(test_file, True)
