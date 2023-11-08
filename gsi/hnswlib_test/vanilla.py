import hnswlib
import numpy as np
import pickle
import pandas as pd 
import datetime
import os

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
#data_path = '/home/gwilliams/Projects/GXL/deep-10M.npy'
data_path = '/mnt/nas1/fvs_benchmark_datasets/deep-1000M.npy'
data = np.load(data_path, allow_pickle=True)
query_path = '/home/gwilliams/Projects/GXL/deep-queries-1000.npy'
queries = np.load(query_path, allow_pickle=True)

# PARSE TO GET NUMRECS
basename = os.path.basename(data_path).split(".")[0]
numrecs = basename.split("-")[1]

# DEFINE VARIABLES
dim = 96
k = 10
num_records = size_num(numrecs)
ef_construction = 64
m = 32
ef_search = 50
results = []

ids = np.arange(num_records)

start_time = datetime.datetime.now()

# Declaring index
p = hnswlib.Index(space = 'cosine', dim = dim) # possible options are l2, cosine or ip

# Initializing index - the maximum number of elements should be known beforehand
p.init_index(max_elements = num_records, ef_construction = ef_construction, M = m)

# Element insertion (can be called several times):
p.add_items(data, ids)

end_time = datetime.datetime.now()


results.append({'operation':'build', 'start_time':start_time, 'end_time':end_time,\
	'walltime':(end_time-start_time).seconds, 'units':'seconds',\
	 'dataset':basename, 'numrecs':num_records,'ef_construction':ef_construction,\
	 'M':m, 'ef_search':-1, 'labels':-1, 'distances':-1})

# Controlling the recall by setting ef:
p.set_ef(ef_search) # ef should always be > k

for query in queries:
	start_time = datetime.datetime.now()
	# Query dataset, k - number of the closest elements (returns 2 numpy arrays)
	labels, distances = p.knn_query(query, k=k)
	end_time = datetime.datetime.now()
	results.append({'operation':'search', 'start_time':start_time, \
	'end_time':end_time, 'walltime':(end_time-start_time).microseconds,\
	'units':'microseconds', 'dataset':basename, 'numrecs':num_records,\
	'ef_construction':-1, 'M':-1, 'ef_search':ef_search, 'labels':labels, \
	'distances':distances})


df = pd.DataFrame(results)
save_path = './results/vanilla_%s_%d_%d_%d.csv'%(basename, ef_construction, m, ef_search)
df.to_csv(save_path, sep="\t")
print("done saving to csv")
df = pd.read_csv(save_path, delimiter="\t")
print(df.head())
