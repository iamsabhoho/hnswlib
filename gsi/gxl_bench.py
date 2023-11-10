#
# configuration
#

# command to get LEDA card information
LEDAGSSH    =   "ledag-ssh -o localhost"

# default location for datasets
DSET_PATH   =   "/mnt/nas1/fvs_benchmark_datasets"  

# default location for GXL utilities
GXL_PATH    =   "/home/gwilliams/Projects/GXL/bin"

# gxl utility to generate centroids
CEN_GEN     =   "run-gxl-cen-gen"

# gxl utility to generate knn graph
KNN_GEN     =   "run-gxl"

# gxl utility to make knn graph symmetric
KNN_MAKE_SYMMETRIC     =   "run-make-symmetric"

# gxl utility to make index
MAKE_INDEX  =   "gxl-hnsw-idx-gen"

# set to True for debugging
VERBOSE     =   True

#
# imports
#
import os
import sys
import glob
import shutil
import argparse
import time
from subprocess import Popen, PIPE, STDOUT, call
import tempfile
from datetime import datetime
import pandas

def get_leda_info( ):
    '''Get LedaG card info.'''

    slots = []

    #
    # This is gnarly code to invoke the ledagssh command,
    # async capture the output, detect the ledagssh prompt, 
    # and send it the quit command, and capture any error
    # code when the process exits.
    #
    cmd = LEDAGSSH.split()
    if VERBOSE: print("\nRunning leda command", cmd, "\n" )
    p = Popen( cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT) 
    os.set_blocking(p.stdout.fileno(), False)
    while True:
        if p.poll()!=None:
            if VERBOSE: print("leda command terminated.")
            if p.returncode!=0:
                print("ERROR: Leda command returned error code %d" % p.returncode)
                return False
            else: break
        b = p.stdout.readline()
        if b==b'':   
            time.sleep(0.01)
            continue
        bs = b.decode('utf-8')
        if VERBOSE: print("leda output: %s" % bs, end="")
        if bs.find("slot")>=0:
            slots.append( bs )
        if bs.startswith("localhost >"):
            if VERBOSE: print()
            p.communicate( str.encode("quit") )

    if VERBOSE: print("ledag slot info:", slots)

    # return number of boards and the board slot details array
    return len(slots), slots

def copy_datasets( workdir, dset ):
    '''Copy datasets from remote/nas locally.'''
   
    # copy fbin
    rpath = os.path.join( DSET_PATH, "%s.fbin" % dset )
    if VERBOSE:  print("Remote fbin path = %s" % rpath)
    cmd = [ "cp", rpath, workdir ]
    if VERBOSE: print("\nRunning cp command", cmd, "\n")
    rcode = call(cmd)
    if rcode!=0:
        print("ERROR: Could not copy file %s to %s" % (rpath ,workdir))
        return False

    # copy lbl
    rpath = os.path.join( DSET_PATH, "%s.lbl" % dset )
    if VERBOSE:  print("Remote lbl path = %s" % rpath)
    cmd = [ "cp", rpath, workdir ]
    if VERBOSE: print("\nRunning cp command", cmd, "\n")
    rcode = call(cmd)
    if rcode!=0:
        print("ERROR: Could not copy file %s to %s" % (rpath ,workdir))
        return False

    return True

def run_cen_gen_utility( workdir, dset ):
    '''Runs the GXL centroids generation utility.'''
    '''usage: run-gxl-cen-gen <db_filename> <optionals: quantization's low_cutoff and high_cutoff>'''

    #
    # This is gnarly code to invoke the GXL command,
    # async capture the output, and capture any error
    # code when the process exits.
    #
    cmd = [ os.path.join( GXL_PATH, CEN_GEN ),  ]
    cmd += [ os.path.join(workdir, "%s.fbin" % dset)  ]
    if VERBOSE: print("\nRunning gxl centroids generation command", cmd, "\n")

    os.chdir(workdir)
    p = Popen( cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=False)
    os.set_blocking(p.stdout.fileno(), False)
    while True:
        if p.poll()!=None:
            if VERBOSE: print("gxl: command terminated.")
            if p.returncode!=0:
                print("ERROR: GXL command returned error code %d" % p.returncode)
                return False
            else: break
        b = p.stdout.readline()
        if b==b'':
            time.sleep(0.01)
            continue
        bs = b.decode('utf-8')
        if VERBOSE: print("gxl: %s" % bs, end="")

    return True

def run_knn_graph_gen_utility( workdir, dset ):
    '''Runs the GXL knn graph generation utility.'''
    '''run-gxl --db <db filename> --cent <centroids filename> [OPTIONS]'''

    #
    # This is gnarly code to invoke the GXL command,
    # async capture the output, and capture any error
    # code when the process exits.
    #
    cmd = [ os.path.join( GXL_PATH, KNN_GEN ),  ]
    cmd += [ "--db", os.path.join(workdir, "%s.fbin" % dset) , "--cent", "./generated_q_centroids.bin"  ]
    if VERBOSE: print("\nRunning gxl knn graph generation command", cmd, "\n")

    os.chdir( workdir )
    p = Popen( cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=False)
    os.set_blocking(p.stdout.fileno(), False)
    while True:
        if p.poll()!=None:
            if VERBOSE: print("gxl: command terminated.")
            if p.returncode!=0:
                print("ERROR: GXL command returned error code %d" % p.returncode)
                return False
            else: break
        b = p.stdout.readline()
        if b==b'':
            time.sleep(0.01)
            continue
        bs = b.decode('utf-8')
        if VERBOSE: print("gxl: %s" % bs, end="")

    return True

def run_knn_make_symmetric_gen_utility( workdir ):
    '''Runs the GXL knn symmetric generation utility.'''
    '''run-make-symmetric <forward_knn_graph_file_name> <distances_file_name> <optional: output_file_name>'''

    #
    # This is gnarly code to invoke the GXL command,
    # async capture the output, and capture any error
    # code when the process exits.
    #
    cmd = [ os.path.join( GXL_PATH, KNN_MAKE_SYMMETRIC ),  ]
    cmd += [ "./knn_graph.bin", "./distances.bin" ]
    if VERBOSE: print("\nRunning gxl make knn graph symmetric generation command", cmd, "\n")

    os.chdir( workdir )
    p = Popen( cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=False)
    os.set_blocking(p.stdout.fileno(), False)
    while True:
        if p.poll()!=None:
            if VERBOSE: print("gxl: command terminated.")
            if p.returncode!=0:
                print("ERROR: GXL command returned error code %d" % p.returncode)
                return False
            else: break
        b = p.stdout.readline()
        if b==b'':
            time.sleep(0.01)
            continue
        bs = b.decode('utf-8')
        if VERBOSE: print("gxl: %s" % bs, end="")

    return True

def run_index_gen_utility( workdir, dset, m, efc ):
    '''Runs the GXL index generation utility.'''
    '''gxl-hnsw-idx-gen <db_filename> <labels_filename> <s_knn_graph_filename> <M> <ef_construction>'''

    #
    # This is gnarly code to invoke the GXL command,
    # async capture the output, and capture any error
    # code when the process exits.
    #
    cmd = [ os.path.join( GXL_PATH, MAKE_INDEX),  ]
    cmd += [ os.path.join(workdir, "%s.fbin" % dset) , os.path.join(workdir, "%s.lbl" % dset)]
    cmd += [ "./s_knn_graph.bin", str(m), str(efc) ]
    if VERBOSE: print("\nRunning gxl make index command", cmd, "\n")

    os.chdir( workdir )
    p = Popen( cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=False)
    os.set_blocking(p.stdout.fileno(), False)
    while True:
        if p.poll()!=None:
            if VERBOSE: print("gxl: command terminated.")
            if p.returncode!=0:
                print("ERROR: GXL command returned error code %d" % p.returncode)
                return False
            else: break
        b = p.stdout.readline()
        if b==b'':
            time.sleep(0.01)
            continue
        bs = b.decode('utf-8')
        if VERBOSE: print("gxl: %s" % bs, end="")

    return True


def move_index( workdir, outdir ):
    '''Move the index file to the output directory.'''

    paths = glob.glob( os.path.join(workdir,"*_gxl.bin") )
    if len(paths)!=1:
        print("ERROR:  Cannot find index file")
        return False

    cmd = [ "mv", paths[0], outdir ]
    if VERBOSE: print("\nRunning mv command", cmd, "\n")
    rcode = call(cmd)
    if rcode!=0:
        print("ERROR: Could not move file %s to %s" % (paths[0] ,outdir))
        return False

    return True
   
def write_results( results, dset, outdir ):
    '''Export the results as a CSV.'''

    df = pandas.DataFrame(results)
    df['dataset'] = dset
    df.to_csv( os.path.join( outdir, "%s.csv" % dset ) )
    print("Wrote timing results to csv file")

def cleanup( workdir, error=False, msg='' ):
    '''Cleanup any temporary dir/file artifacts.'''
    '''If error==True, then raise an exception.'''

    if VERBOSE: print("Removing directory %s" % workdir)

    shutil.rmtree(workdir)

    if error: raise Exception("%s" % msg)

if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser("gxl benchmarking tool.")
    parser.add_argument('-u','--gxl_utilities_path',  default=GXL_PATH)
    parser.add_argument('-n','--npy_path', default=DSET_PATH)
    parser.add_argument('-d','--dataset', required=True,help="dataset name like 'deep-10M'")
    parser.add_argument('-m',type=int, default=32) 
    parser.add_argument('-e',type=int, default=64) # ef construction
    parser.add_argument('-o','--output', required=True, help="output directory")
    args = parser.parse_args()

    # get leda card info
    num_boards, board_details = get_leda_info()
    print("\nFound %d boards" % num_boards)
    if num_boards==0:
        raise Exception("ERROR: Could not find any APU boards")

    # get the current working dir
    curdir = os.getcwd()

    # create a temp working dir
    tmpdir = tempfile.mkdtemp()
    os.chmod(tmpdir,0o777)
    print('Created temporary directory', tmpdir)

    # copy datasets locally
    if not copy_datasets( tmpdir, args.dataset ):
        cleanup(tmpdir, error=True, msg="ERROR: Could not copy datasets.")

    # collect timings
    results = []

    # run centroids generation
    s = datetime.now()
    if not run_cen_gen_utility( tmpdir, args.dataset ):
        cleanup(tmpdir, error=True, msg="ERROR: Could not generate centroids.")
    e = datetime.now()
    print("cen gen walltime=", (e-s).total_seconds())
    results.append( {'operation':'build-index', 'subop':'cen_gen', 'start':s, 'end':e, 'walltime': (e-s).total_seconds()} )
 
    # run knn graph generation
    s = datetime.now()
    if not run_knn_graph_gen_utility( tmpdir, args.dataset ):
        cleanup(tmpdir, error=True, msg="ERROR: Could not generate knn graph.")
    e = datetime.now()
    print("knn gen walltime=", (e-s).total_seconds())
    results.append( {'operation':'build-index', 'subop':'knn_gen', 'start':s, 'end':e, 'walltime': (e-s).total_seconds()} )
 
    # make knn graph symmetric
    s = datetime.now()
    if not run_knn_make_symmetric_gen_utility( tmpdir ):
        cleanup(tmpdir, error=True, msg="ERROR: Could not make knn graph symmetric.")
    e = datetime.now()
    print("knn symmmetric walltime=", (e-s).total_seconds())
    results.append( {'operation':'build-index', 'subop':'knn_symmetric', 'start':s, 'end':e, 'walltime': (e-s).total_seconds()} )
    
    # make the index
    s = datetime.now()
    if not run_index_gen_utility( tmpdir, args.dataset, args.m, args.e ):
        cleanup(tmpdir, error=True, msg="ERROR: Could not generate the index.")
    e = datetime.now()
    print("make index walltime=", (e-s).total_seconds())
    results.append( {'operation':'build-index', 'subop':'index_gen', 'start':s, 'end':e, 'walltime': (e-s).total_seconds()} )

    # finalize
    os.chdir( curdir )
    move_index(tmpdir, args.output)
    write_results(results, args.dataset, args.output )
    cleanup(tmpdir)
    print("Done.  Generated index is at %s" % args.output)

    sys.exit(0)
