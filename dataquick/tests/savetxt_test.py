import os
import dataquick.plugins.examples as ex
df = ex.example_powderdiffraction()
test_file = os.path.join(os.path.expanduser("~"), "Documents/test.dqf")
df.savetxt(test_file, True)
