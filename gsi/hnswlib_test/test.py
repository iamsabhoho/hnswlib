import hnswlib
import numpy as np

data_path = '/home/gwilliams/Projects/GXL/deep-10M.npy'

dim = 768
num_elements = 10000000

# load data
print("loading data... '%s'" % data_path)
data = np.load(data_path, allow_pickle=True)
print("done loading ...")

print(data.shape)
print(data[0].shape)
print(data[0][0].shape)
