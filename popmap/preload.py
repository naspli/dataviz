import os

import numpy as np
from dask.array.image import imread
from numba import njit

data_dir = "data"
worldpop_file = "ppp_2020_1km_Aggregated.tif"
reduction_factor = 15

dask_arr = imread(os.path.join(data_dir, worldpop_file))
X = np.array(dask_arr[0])
X = np.clip(X, a_min=0, a_max=None)

Xreduce = np.zeros([n // reduction_factor for n in X.shape])


@njit
def reduce_resolution(X, Xreduce, reduction_factor):
    N = X.shape[0]
    M = X.shape[1]
    for i in range(N):
        for j in range(M):
            ii = i // reduction_factor
            jj = j // reduction_factor
            Xreduce[ii, jj] = Xreduce[ii, jj] + X[i, j]
    return Xreduce


Xreduce = reduce_resolution(X, Xreduce, reduction_factor)
out_file = f"popmap_{reduction_factor}.npy"
np.save(os.path.join(data_dir, out_file), Xreduce)