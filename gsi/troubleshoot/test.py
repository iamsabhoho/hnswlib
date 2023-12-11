# This program tries to troubleshoot why we are seeing different behavior
# when we search q-by-q using a GXL index vs a "vanilla" HNSW index.

# The "vanilla" HNSWLib EF construction parameter
EFC = 64

# The "graph connectivity" M value
M = 32

# Size of Deep1B subset to test
NUM_RECORDS = 100000000

# string version of subset num_records - add more as you need them
NUM_REC_STR = "1m" if NUM_RECORDS==1000000 else \
    ( "100m" if NUM_RECORDS==100000000 else "=1" )

# Path to the GXL built index
GXL_INDEX_PATH = \
    "/mnt/nas1/GXL/deep1B/v2.0_with250Mfix/deep1B_%s_ef_%d_M_%d_gxl.bin" % \
        ( NUM_REC_STR, EFC, M )

# Path to the dataset (numpy)
DEEP1B_DATASET = "/mnt/nas1/fvs_benchmark_datasets/deep-%s.npy" % NUM_REC_STR.upper()

# Path to the queries (numpy)
DEEP1B_QUERIES = "/home/gwilliams/Projects/GXL/deep-queries-1000.npy"

# Path to the queries ground truth
DEEP1B_QUERIES_GT = "/mnt/nas1/fvs_benchmark_datasets/deep-%s-gt-1000.npy" % NUM_REC_STR.upper()

# The vector dimensions of Deep1B
DIMS = 96

# EF search paramters to test
EF_SEARCHES = [64, 128, 256, 512]

VERBOSE = False

#
# imports
#
import sys
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
    vanilla_recalls = {}
    vanilla_latencies = {}

    for ef_search in EF_SEARCHES:
        vanilla_recalls[ef_search] = []
        vanilla_latencies[ef_search] = []

        # Change ef_search parameter
        p.set_ef(ef_search) 
    
        for i, query in enumerate(queries):

            # Do the 1-query search
            start_time = datetime.datetime.now()
            labels, distances = p.knn_query(query, k=10)
            end_time = datetime.datetime.now()
        
            # compute latency in milliseconds
            latency = (end_time - start_time).total_seconds() * 1000
            if VERBOSE: print("For ef_search=%d, query_index=%d: latency=%d ms" % (ef_search, i, latency))
            vanilla_latencies[ef_search].append(latency)
    
            # compute recall
            recall =  compute_recall( gt[i][0:10].reshape((1,10)), labels.reshape((1,10)) )[0]
            if VERBOSE: print("For ef_search=%d, query_index=%d: recall=%f ms" % (ef_search, i, recall))
            vanilla_recalls[ef_search].append(recall)

        print("Vanilla index: For ef_search=%d, mean recall=%f, mean latency=%f" % \
            (ef_search, np.mean( vanilla_recalls[ef_search] ), np.mean( vanilla_latencies[ef_search] ) ) )
    print("Searches done.")

    # load the GXL index
    print()
    print("Loading GXL index from", GXL_INDEX_PATH )
    gxl = hnswlib.Index(space='cosine', dim=DIMS)
    gxl.load_index(GXL_INDEX_PATH, max_elements=NUM_RECORDS)
    print("Load done.")

    # loop on queries, accumulate recall and latency
    print("Now performing searches on GXL index.")
    gxl_recalls = {}
    gxl_latencies = {}

    for ef_search in EF_SEARCHES:
        gxl_recalls[ef_search] = []
        gxl_latencies[ef_search] = []

        # Change ef_search paramter
        gxl.set_ef(ef_search)

        for i, query in enumerate(queries):

            # Do the 1-query search
            start_time = datetime.datetime.now()
            labels, distances = gxl.knn_query(query, k=10)
            end_time = datetime.datetime.now()

            # compute latency in milliseconds
            latency = (end_time - start_time).total_seconds() * 1000
            if VERBOSE: print("For ef_search=%d, query_index=%d: latency=%d ms" % (ef_search, i, latency))
            gxl_latencies[ef_search].append(latency)

            # compute recall
            recall =  compute_recall( gt[i][0:10].reshape((1,10)), labels.reshape((1,10)) )[0]
            if VERBOSE: print("For ef_search=%d, query_index=%d: recall=%f ms" % (ef_search, i, recall))
            gxl_recalls[ef_search].append(recall)

        print("GXL index: For ef_search=%d, mean recall=%f, mean latency=%f" % \
            (ef_search, np.mean( gxl_recalls[ef_search] ), np.mean( gxl_latencies[ef_search] ) ) )

    print("Searches done.")

    # Print a nicely formatted table so we can compare easily
    print()
    print()
    print("Deep1B (%s subset) Search Comparison" % NUM_REC_STR )
    print()
    cols_format = "{0:<10} {1:<10} {2:<10} {3:<10}"
    print( cols_format.format( *["ef_search","index","recall","latency(ms)"]))
    print( "------------------------------------------")
    for ef_search in EF_SEARCHES:
        print( cols_format.format( *["%d" % ef_search,"vanilla",\
            "%.2f" % np.mean(vanilla_recalls[ef_search]), \
            "%.2f" % np.mean(vanilla_latencies[ef_search]) ]))
        print( cols_format.format( *["","gxl",\
            "%1.2f" % np.mean(gxl_recalls[ef_search]), \
            "%.2f" % np.mean(gxl_latencies[ef_search]) ]))
  
    print() 
    print("Done.") 
    
if __name__ == "__main__":
    '''This gets run if this gets run as a CLI program.'''

    test()

