import hnswlib
import numpy as np
import pandas as pd
import datetime
import os

k = 10
dim = 96
ef_search = [64, 128, 256, 512]
results = []

#index_dir = '/mnt/nas1/GXL/deep1B/v2.0_with250Mfix/'
index_dir = '/tmp/gxl_1702413856/'
filename = 'deep1B_1000m_ef_64_M_32_gxl.bin'
index_path = os.path.join(index_dir, filename)
#data_path = '/home/gwilliams/Projects/GXL/deep-10M.npy'
data_path = '/mnt/nas1/fvs_benchmark_datasets/deep-1000M.npy'
#index_path = '/home/gwilliams/Projects/GXL/deep1B_50m_ef_64_M_32_gxl.bin'
query_path = '/home/gwilliams/Projects/GXL/deep-queries-1000.npy'
queries = np.load(query_path, allow_pickle=True)

def size_num(s):
    '''get raw numercs of text abbrev'''
    if s == '1m': return 1000000
    elif s == '2M': return 2000000
    elif s == '5M': return 5000000
    elif s == '10m': return 10000000
    elif s == '20m': return 20000000
    elif s == '50m': return 50000000
    elif s == '100m': return 100000000
    elif s == '200M': return 200000000
    elif s == '250m': return 250000000
    elif s == '500m': return 500000000
    elif s == '10K': return 10000
    elif s == '1000m': return 1000000000
    else: raise Exception("Unsupported size " + s)

# parse parameters
basename = os.path.basename(index_path).split(".")[0]
params = basename.split("_")
dataset = params[0]
numrecs = params[1] 
ef_construction = params[3]
m = params[5]
num_records = size_num(numrecs)

start_time = datetime.datetime.now()

p = hnswlib.Index(space='cosine', dim=dim)
print("\nLoading index from '%s'\n" % index_path)
p.load_index(index_path, max_elements=num_records)
print("done loading index")

end_time = datetime.datetime.now()
results.append({'operation':'load', 'start_time':start_time, 'end_time':end_time,\
 	'walltime':(end_time-start_time).total_seconds(), 'units':'seconds', 'dataset':dataset, 'numrecs':num_records,\
	'ef_construction':ef_construction, 'M':m, 'ef_search':-1, 'labels':-1, 'distances':-1})

for ef in ef_search:
    p.set_ef(ef)
    # knn query
    for query in queries:
        start_time = datetime.datetime.now()
        labels, distances = p.knn_query(query, k=k)
        end_time = datetime.datetime.now()
        results.append({'operation':'search', 'start_time':start_time, 'end_time':end_time,\
            'walltime':((end_time-start_time).total_seconds() * 1000 ), 'units':'milliseconds', 'dataset':dataset,\
            'numrecs':num_records, 'ef_construction':-1, 'M':-1,\
            'ef_search':ef, 'labels':labels, 'distances':distances})

df = pd.DataFrame(results)
save_path = './results/gxl_numactl_load_%s_%d.csv'%(basename, ef)
df.to_csv(save_path, sep="\t")
print("done saving to csv")
df = pd.read_csv(save_path, delimiter='\t')
print(df.head())

