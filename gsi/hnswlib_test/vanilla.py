import hnswlib
import numpy as np
import pickle
import pandas as pd 
import datetime

dim = 96
num_elements = 10000000
k = 5
results = []


# Generating sample data
data_path = '/home/gwilliams/Projects/GXL/deep-10M.npy'
data = np.load(data_path, allow_pickle=True)
query_path = '/home/gwilliams/Projects/GXL/deep-queries-1.npy'
query = np.load(query_path, allow_pickle=True)

ids = np.arange(num_elements)

start_time = datetime.datetime.now()

# Declaring index
p = hnswlib.Index(space = 'cosine', dim = dim) # possible options are l2, cosine or ip

# Initializing index - the maximum number of elements should be known beforehand
p.init_index(max_elements = num_elements, ef_construction = 64, M = 32)

# Element insertion (can be called several times):
p.add_items(data, ids)

# Controlling the recall by setting ef:
p.set_ef(50) # ef should always be > k

end_time = datetime.datetime.now()

# Query dataset, k - number of the closest elements (returns 2 numpy arrays)
labels, distances = p.knn_query(query, k = k)

# Index objects support pickling
# WARNING: serialization via pickle.dumps(p) or p.__getstate__() is NOT thread-safe with p.add_items method!
# Note: ef parameter is included in serialization; random number generator is initialized with random_seed on Index load
p_copy = pickle.loads(pickle.dumps(p)) # creates a copy of index p using pickle round-trip

### Index parameters are exposed as class properties:
print(f"Parameters passed to constructor:  space={p_copy.space}, dim={p_copy.dim}") 
print(f"Index construction: M={p_copy.M}, ef_construction={p_copy.ef_construction}")
print(f"Index size is {p_copy.element_count} and index capacity is {p_copy.max_elements}")
print(f"Search speed/quality trade-off parameter: ef={p_copy.ef}")
print("labels: ", labels)
print("distances: ", distances)
