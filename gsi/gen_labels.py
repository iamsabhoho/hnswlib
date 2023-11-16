
import numpy as np
import os
from struct import *

# configure this array with path to numpy files you want converted to fbin
FILES = [ "deep-1M.fbin", "deep-10M.fbin", "deep-20M.fbin", "deep-50M.fbin", "deep-100M.fbin", "deep-250M.fbin" ]


for file in FILES:

    # form the name of the converted output file
    fname = os.path.basename(file).split(".")[0]
    fout = fname + ".lbl"
    fpath = os.path.join( os.path.dirname(file), fout )
    if os.path.exists(fpath):
        print("WARNING: path %s already exists" % fpath )
        continue

    f = open(file,"rb")
    header = f.read(8)
    vals = unpack("<II", header)
    print("header=", vals)
    f.close()
    print("size=", vals[0])


    # open lbl file for write
    f = open(fpath,"wb")

    # create the fbin header
    header = pack("<II", vals[0], 8)
    print("header bytes =",len(header))

    # write header
    f.write(header)

    # loop on array elements
    for i in range(vals[0]):
        if i % 1000 == 0:  print("writing %d/%d" % (i+1, vals[0]) )
        fval_out = pack("<Q", i)
        f.write(fval_out)

    f.flush()
    f.close()
    print("Closed %s" % fpath)


