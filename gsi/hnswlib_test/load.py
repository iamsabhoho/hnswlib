import hnswlib
import numpy as np
import pandas as pd
import datetime
import os

k = 10
dim = 96
ef_search = 50
results = []

data_path = '/home/gwilliams/Projects/GXL/deep-10M.npy'
index_path = '/home/gwilliams/Projects/GXL/deep1B_10m_ef_64_M_32_gxl.bin'
query_path = '/home/gwilliams/Projects/GXL/deep-queries-1000.npy'
queries = np.load(query_path, allow_pickle=True)

# parse parameters
basename = os.path.basename(index_path).split(".")[0]
params = basename.split("_")
dataset = params[0]
numrecs = params[1] 
ef_construction = params[3]
m = params[5]

if numrecs == '10m':
	num_records = 10000000 
else:
	raise Exeception("not implemented")

start_time = datetime.datetime.now()

p = hnswlib.Index(space='cosine', dim=dim)
print("\nLoading index from '%s'\n" % index_path)
p.load_index(index_path, max_elements=num_records)
print("done loading index")

end_time = datetime.datetime.now()
results.append({'operation':'load', 'start_time':start_time, 'end_time':end_time,\
 	'walltime':(end_time-start_time).seconds, 'units':'seconds', 'dataset':dataset, 'numrecs':num_records,\
	'ef_construction':ef_construction, 'M':m, 'ef_search':-1, 'labels':-1, 'distances':-1})

p.set_ef(ef_search)
# knn query
for query in queries:
	start_time = datetime.datetime.now()
	labels, distances = p.knn_query(query, k=k)
	end_time = datetime.datetime.now()
	results.append({'operation':'search', 'start_time':start_time, 'end_time':end_time,\
 		'walltime':(end_time-start_time).microseconds, 'units':'microseconds', 'dataset':dataset,\
		'numrecs':num_records, 'ef_construction':-1, 'M':-1,\
		'ef_search':ef_search, 'labels':labels, 'distances':distances})

df = pd.DataFrame(results)
save_path = './results/gxl_load_%s_%d.csv'%(basename, ef_search)
df.to_csv(save_path, sep="\t")
print("done saving to csv")
df = pd.read_csv(save_path, delimiter='\t')
print(df.head())

