import hnswlib
import numpy as np
import pickle
import pandas as pd 
import datetime
import os
import psutil

# This script shows an example of building and searching Deep1B-1000M with HNSWLIB

def size_num(s):
    '''get raw numercs of text abbrev'''
    if s == '1M': return 1000000
    elif s == '2M': return 2000000
    elif s == '5M': return 5000000
    elif s == '10M': return 10000000
    elif s == '20M': return 20000000
    elif s == '50M': return 50000000
    elif s == '100M': return 100000000
    elif s == '200M': return 200000000
    elif s == '250M': return 250000000
    elif s == '500M': return 500000000
    elif s == '10K': return 10000
    elif s == '1000M': return 1000000000
    else: raise Exception("Unsupported size " + s)

# GET PATH and LOAD FILES
data_path = '/mnt/nas1/fvs_benchmark_datasets/deep-1000M.npy'
data = np.load(data_path, allow_pickle=True)
query_path = '/home/gwilliams/Projects/GXL/deep-queries-1000.npy'
queries = np.load(query_path, allow_pickle=True)

# PARSE TO GET NUMRECS
basename = os.path.basename(data_path).split(".")[0]
numrecs = basename.split("-")[1]

# DEFINE VARIABLES
# Change the following parameters as needed
dim = 96
k = 10
num_records = size_num(numrecs)
ef_construction = 64
m = 32
ef_search = [64, 128, 256, 512]
results = []

ids = np.arange(num_records)

process = psutil.Process()

start_time = datetime.datetime.now()
print("declaring index... ", process.memory_info().rss)
# Declaring index
p = hnswlib.Index(space = 'cosine', dim = dim) # possible options are l2, cosine or ip

# Initializing index - the maximum number of elements should be known beforehand
p.init_index(max_elements = num_records, ef_construction = ef_construction, M = m)

# Element insertion (can be called several times):
p.add_items(data, ids)

end_time = datetime.datetime.now()
print("appending results... ", process.memory_info().rss)



results.append({'operation':'build', 'start_time':start_time, 'end_time':end_time,\
	'walltime':(end_time-start_time).total_seconds(), 'units':'seconds',\
	 'dataset':basename, 'numrecs':num_records,'ef_construction':ef_construction,\
	 'M':m, 'ef_search':-1, 'labels':-1, 'distances':-1})

# Saving Index
"""
save_index_dir = './results/vanilla_idx/'
filename_idx = '%s_ef_%d_M_%d_vanilla.bin'%(basename, ef_construction, m)
save_index_path = os.path.join(save_index_dir, filename_idx)
print("saving index to '%s'" % save_index_path)
p.save_index(save_index_path)
print('done saving index...')
"""

print("searching now...")
# Controlling the recall by setting ef:
for ef in ef_search:
    p.set_ef(ef) # ef should always be > k

    print("ef: ", ef)
    print(process.memory_info().rss)
    for query in queries:
        start_time = datetime.datetime.now()
        # Query dataset, k - number of the closest elements (returns 2 numpy arrays)
        labels, distances = p.knn_query(query, k=k)
        end_time = datetime.datetime.now()
        results.append({'operation':'search', 'start_time':start_time, \
        'end_time':end_time, 'walltime':((end_time-start_time).total_seconds() * 1000 ),\
        'units':'milliseconds', 'dataset':basename, 'numrecs':num_records,\
        'ef_construction':-1, 'M':-1, 'ef_search':ef, 'labels':labels, \
        'distances':distances})


print("done... appending to df...")

df = pd.DataFrame(results)
save_path = './results/vanilla_%s_%d_%d_%d.csv'%(basename, ef_construction, m, ef)
df.to_csv(save_path, sep="\t")
print("done saving to csv")
df = pd.read_csv(save_path, delimiter="\t")
print(df.head())
