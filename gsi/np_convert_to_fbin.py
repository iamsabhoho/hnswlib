import numpy as np
import os
from struct import *

# configure this array with path to numpy files you want converted to fbin
FILES = ["deep-1M.npy", "deep-10M.npy", "deep-20M.npy", "deep-50M.npy", "deep-100M.npy", "deep-250M.npy" ]

# loop through input files and convert to fbin
for file in FILES:

    # form the name of the converted output file
    fname = os.path.basename(file).split(".")[0]
    fout = fname + ".fbin"
    fpath = os.path.join( os.path.dirname(file), fout )
    if os.path.exists(fpath):
        print("WARNING: path %s already exists" % fpath )
        continue

    # load the numpy file
    arr = np.load(file)
    print("numpy input file", file, arr.shape, arr.size, arr.dtype )

    f = open(fpath,"wb")
    print("Opened %s for writing..." % fpath)
    
    # create the fbin header
    header = pack("<II", arr.shape[0], arr.shape[1])
    print("header bytes =",len(header)) 

    # write header
    f.write(header)

    # loop on array elements
    for i in range(arr.shape[0]):
        if i % 1000 == 0:  print("writing %d/%d" % (i+1, arr.shape[0]) )
        elin = arr[i]
        for d in range(arr.shape[1]):
            fval_in = elin[d]
            fval_out = pack("<f", fval_in)
            f.write(fval_out)

    f.flush()
    f.close()
    print("Closed %s" % fpath)

    print("Validating...")
    f = open(fpath,"rb")
    header = f.read(8)
    vals = unpack("<II", header)
    print("header=", vals)
    f.close()

    m = np.memmap( fpath, dtype=np.float32, offset=8, shape=(arr.shape[0],arr.shape[1]) )
    print(m.shape, m.dtype)
    first = m[0]
    print( "first", first.shape, arr[0].shape, first[0],arr[0][0], first[ arr.shape[1]-1 ], arr[0][arr.shape[1]-1] )
    last = m[-1]
    print( "last", last.shape, arr[-1].shape, last[0],arr[-1][0])
    
