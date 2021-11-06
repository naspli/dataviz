import os

import matplotlib.pyplot as plt
import numpy as np

data_dir = "data"
data_file = "popmap_15.npy"

X = np.load(os.path.join(data_dir, data_file))
plt.imshow(np.log(X + 0.01))
plt.show()