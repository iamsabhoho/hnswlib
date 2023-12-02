# This program tries to troubleshoot why we are seeing different behavior
# when we search q-by-q using a GXL index vs a "vanilla" HNSW index.

# Path to the GXL built index
GXL_INDEX_PATH = "/mnt/nas1/GXL/deep1B/v2.0_with250Mfix/deep1B_1m_ef_64_M_32_gxl.bin"

# Path to the dataset (numpy)
DEEP1B_DATASET = "/mnt/nas1/fvs_benchmark_datasets/deep-1M.npy"

# Path to the queries (numpy)
DEEP1B_QUERIES = "/home/gwilliams/Projects/GXL/deep-queries-1000.npy"

# Path to the queries ground truth
DEEP1B_QUERIES_GT = "/mnt/nas1/fvs_benchmark_datasets/deep-1M-gt-1000.npy"

# The "vanilla" HNSWLib EF construction parameter
EFC = 64

# The "graph connectivity" M value
M = 32

# The dimensions of Deep1B
DIMS = 96

# Size of Deep1B subset
NUM_RECORDS = 1000000

# EF search paramters to test
EF_SEARCHES = [64, 128, 256, 512]

VERBOSE = False

#
# imports
#
import numpy as np
import datetime
import hnswlib

def compute_recall(a, b):
    '''Computes the recall metric on query results.'''
    
    if VERBOSE: print("input shapes:", a.shape, b.shape)

    nq, rank = a.shape
    intersect = [ np.intersect1d(a[i, :rank], b[i, :rank]).size for i in range(nq) ]
    ninter = sum( intersect )
    return ninter / a.size, intersect


def test():
    '''This will create a Deep-1B(subset) HNSWLib index via GXL or normal ('vanilla' )'''
    '''and compare the q-b-q search performance.'''

    # load the datasetA
    print()
    print("Loading dataset from %s" % DEEP1B_DATASET)
    data = np.load( DEEP1B_DATASET, allow_pickle=True)
    print("Load done, shape=", data.shape)

    # load the queries
    queries = np.load( DEEP1B_QUERIES, allow_pickle=True )
    print("Loaded queries, shape=", queries.shape)

    # load the queries ground truth
    gt = np.load( DEEP1B_QUERIES_GT, allow_pickle=True ).reshape((1000,100))
    print("Loaded ground truth, shape=", gt.shape)
    print()

    # hnswlib needs label ids
    ids = np.arange(NUM_RECORDS)

    # build the index the 'vanilla' way
    print("Building vanilla HNSWLib index for  %s" % DEEP1B_DATASET)
    p = hnswlib.Index(space = 'cosine', dim = DIMS) 
    p.init_index(max_elements = NUM_RECORDS, ef_construction = EFC, M = M)
    p.add_items(data, ids)
    print("Build done.")

    # loop on queries, accumulate recall and latency
    print("Now performing searches on vanilla index.")
    for ef_search in EF_SEARCHES:
        recalls = []
        latencies = []

        p.set_ef(ef_search) 
    
        for i, query in enumerate(queries):

            # Do the 1-query search
            start_time = datetime.datetime.now()
            labels, distances = p.knn_query(query, k=10)
            end_time = datetime.datetime.now()
        
            # compute latency in milliseconds
            latency = (end_time - start_time).total_seconds() * 1000
            if VERBOSE: print("For ef_search=%d, query_index=%d: latency=%d ms" % (ef_search, i, latency))
            latencies.append(latency)
    
            # compute recall
            recall =  compute_recall( gt[i][0:10].reshape((1,10)), labels.reshape((1,10)) )[0]
            if VERBOSE: print("For ef_search=%d, query_index=%d: recall=%f ms" % (ef_search, i, recall))
            recalls.append(recall)

        print("Vanilla index: For ef_search=%d, mean recall=%f, mean latency=%f" % \
            (ef_search, np.mean( recalls ), np.mean( latencies ) ) )
    print("Searches done.")

    # load the GXL index
    print()
    print("Loading GXL index from", GXL_INDEX_PATH )
    gxl = hnswlib.Index(space='cosine', dim=DIMS)
    gxl.load_index(GXL_INDEX_PATH, max_elements=NUM_RECORDS)
    print("Load done.")

    # loop on queries, accumulate recall and latency
    print("Now performing searches on GXL index.")
    for ef_search in EF_SEARCHES:
        recalls = []
        latencies = []

        gxl.set_ef(ef_search)

        for i, query in enumerate(queries):

            # Do the 1-query search
            start_time = datetime.datetime.now()
            labels, distances = gxl.knn_query(query, k=10)
            end_time = datetime.datetime.now()

            # compute latency in milliseconds
            latency = (end_time - start_time).total_seconds() * 1000
            if VERBOSE: print("For ef_search=%d, query_index=%d: latency=%d ms" % (ef_search, i, latency))
            latencies.append(latency)

            # compute recall
            recall =  compute_recall( gt[i][0:10].reshape((1,10)), labels.reshape((1,10)) )[0]
            if VERBOSE: print("For ef_search=%d, query_index=%d: recall=%f ms" % (ef_search, i, recall))
            recalls.append(recall)

        print("GXL index: For ef_search=%d, mean recall=%f, mean latency=%f" % \
            (ef_search, np.mean( recalls ), np.mean( latencies ) ) )

    print("Searches done.")

    
if __name__ == "__main__":
    '''This gets run if this gets run as a CLI program.'''

    test()

