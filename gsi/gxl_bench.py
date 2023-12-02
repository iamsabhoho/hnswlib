#
# configuration
#

# command to get LEDA card information
LEDAGSSH    =   "ledag-ssh -o localhost"

# default search location for datasets
DSET_LOCAL  =   "/home/gwilliams/Projects/GXL"
DSET_REMOTE =   "/mnt/nas1/fvs_benchmark_datasets"

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
from subprocess import Popen, PIPE, STDOUT, call, check_output
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

def get_datasets( workdir, dset ):
    ''' Get fbin/lbl datasets from remote/nas local working dir.
        Copy as needed.'''

    # fbin, try local first
    fbin_path = os.path.join( DSET_LOCAL, "%s.fbin" % dset )
    if not os.path.exists(fbin_path):
        # copy from remote
        fbin_path = os.path.join( DSET_REMOTE, "%s.fbin" % dset )
        cmd = [ "cp", fbin_path, workdir ]
        if VERBOSE: print("\nRunning cp command", cmd, "\n")
        rcode = call(cmd)
        if rcode!=0:
            print("ERROR: Could not copy file %s to %s" % (fbin_path ,workdir))
            return False

    # lbl, try local first
    lbl_path = os.path.join( DSET_LOCAL, "%s.lbl" % dset )
    if not os.path.exists(lbl_path):
        # copy from remote
        lbl_path = os.path.join( DSET_REMOTE, "%s.lbl" % dset )
        cmd = [ "cp", lbl_path, workdir ]
        if VERBOSE: print("\nRunning cp command", cmd, "\n")
        rcode = call(cmd)
        if rcode!=0:
            print("ERROR: Could not copy file %s to %s" % (lbl_path ,workdir))
            return False
    
    return fbin_path, lbl_path

def get_cen_gen_version():
    '''Retrieve the version of the centroids generation utility.'''

    cmd = [ os.path.join( GXL_PATH, CEN_GEN ), "--version" ]
    if VERBOSE: print("\nGetting gxl centroids generation version", cmd, "\n")

    p = check_output( cmd ) 
    vers = p.decode('utf-8').replace("\n","")
    if VERBOSE: print("version=", vers)
    return vers 

def run_cen_gen_utility( cpunodebind, preferred, workdir, fbin_path ):
    '''Runs the GXL centroids generation utility.'''
    '''usage: run-gxl-cen-gen <db_filename> <optionals: quantization's low_cutoff and high_cutoff>'''

    #
    # This is gnarly code to invoke the GXL command,
    # async capture the output, and capture any error
    # code when the process exits.
    #
    cmd = [ os.path.join( GXL_PATH, CEN_GEN ),  ]
    cmd += [ fbin_path  ]
    if cpunodebind!=None and preferred!=None:
        cmd = [ "numactl", "--cpunodebind=%d" % cpunodebind, "--preferred=%d" % preferred ]  + cmd
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

def get_knn_graph_gen_version():
    '''Retrieve the version of the knn graph generation utility.'''

    cmd = [ os.path.join( GXL_PATH, KNN_GEN ), "--version" ]
    if VERBOSE: print("\nGetting gxl knn graph generation version", cmd, "\n")

    p = check_output( cmd )
    vers = p.decode('utf-8').replace("\n","")
    if VERBOSE: print("version=", vers)
    return vers

def run_knn_graph_gen_utility( cpunodebind, preferred, workdir, fbin_path ):
    '''Runs the GXL knn graph generation utility.'''
    '''run-gxl --db <db filename> --cent <centroids filename> [OPTIONS]'''

    #
    # This is gnarly code to invoke the GXL command,
    # async capture the output, and capture any error
    # code when the process exits.
    #
    cmd = [ os.path.join( GXL_PATH, KNN_GEN ),  ]
    cmd += [ "--db", fbin_path , "--cent", "./generated_q_centroids.bin"  ]
    if cpunodebind!=None and preferred!=None:
        cmd = [ "numactl", "--cpunodebind=%d" % cpunodebind, "--preferred=%d" % preferred ]  + cmd
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

def get_knn_make_symmetric_gen_version():
    '''Retrieve the version of the knn make symmetric generation utility.'''

    cmd = [ os.path.join( GXL_PATH, KNN_MAKE_SYMMETRIC ), "--version" ]
    if VERBOSE: print("\nGetting gxl knn make symmetric generation version", cmd, "\n")

    p = check_output( cmd )
    vers = p.decode('utf-8').replace("\n","")
    if VERBOSE: print("version=", vers)
    return vers

def run_knn_make_symmetric_gen_utility( cpunodebind, preferred, workdir ):
    '''Runs the GXL knn symmetric generation utility.'''
    '''run-make-symmetric <forward_knn_graph_file_name> <distances_file_name> <optional: output_file_name>'''

    #
    # This is gnarly code to invoke the GXL command,
    # async capture the output, and capture any error
    # code when the process exits.
    #
    cmd = [ os.path.join( GXL_PATH, KNN_MAKE_SYMMETRIC ),  ]
    cmd += [ "./knn_graph.bin", "./distances.bin" ]
    if cpunodebind!=None and preferred!=None:
        cmd = [ "numactl", "--cpunodebind=%d" % cpunodebind, "--preferred=%d" % preferred ]  + cmd
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

def get_make_index_gen_version():
    '''Retrieve the version of the make index generation utility.'''

    cmd = [ os.path.join( GXL_PATH, MAKE_INDEX ), "--version" ]
    if VERBOSE: print("\nGetting gxl make index generation version (file size)", cmd, "\n")

    sz = os.path.getsize( os.path.join( GXL_PATH, MAKE_INDEX ) )
    vers = "exesize="+str(sz)
    if VERBOSE: print(vers)
    return vers

def run_index_gen_utility( cpunodebind, preferred, workdir, fbin_path, lbl_path, m, efc ):
    '''Runs the GXL index generation utility.'''
    '''gxl-hnsw-idx-gen <db_filename> <labels_filename> <s_knn_graph_filename> <M> <ef_construction>'''

    #
    # This is gnarly code to invoke the GXL command,
    # async capture the output, and capture any error
    # code when the process exits.
    #
    cmd = [ os.path.join( GXL_PATH, MAKE_INDEX),  ]
    cmd += [ fbin_path, lbl_path ]
    cmd += [ "./s_knn_graph.bin", str(m), str(efc) ]
    if cpunodebind!=None and preferred!=None:
        cmd = [ "numactl", "--cpunodebind=%d" % cpunodebind, "--preferred=%d" % preferred ]  + cmd
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

def remove_index( workdir, outdir ):
    '''Remove the index file.'''

    paths = glob.glob( os.path.join(workdir,"*_gxl.bin") )
    if len(paths)!=1:
        print("ERROR:  Cannot find index file")
        return False

    cmd = [ "rm", paths[0] ]
    if VERBOSE: print("\nRunning rm command", cmd, "\n")
    rcode = call(cmd)
    if rcode!=0:
        print("ERROR: Could not remove file %s to %s" % (paths[0] ,outdir))
        return False


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

    return os.path.join( outdir, os.path.basename(paths[0]) )
   
def write_results( results, dset, outdir ):
    '''Export the results as a CSV.'''

    df = pandas.DataFrame(results)
    df['dataset'] = dset
    ts = datetime.now().timestamp()
    fpath = os.path.join( outdir, "%s_%f.csv" % (dset,ts))
    df.to_csv( fpath, sep='\t')
    print("Wrote timing results to csv file to", fpath)

def cleanup( workdir, error=False, msg='' ):
    '''Cleanup any temporary dir/file artifacts.'''
    '''If error==True, then raise an exception.'''

    if VERBOSE: print("Removing temporary directory %s" % workdir)

    shutil.rmtree(workdir)

    if error: raise Exception("%s" % msg)

if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser("gxl benchmarking tool.")
    parser.add_argument('-d','--dataset', required=True,help="dataset name like 'deep-10M'")
    parser.add_argument('-m',type=int, default=32) 
    parser.add_argument('-e',type=int, default=64) # ef construction
    parser.add_argument('-o','--output', required=True, help="output directory")
    parser.add_argument('-c','--cpunodebind', type=int)
    parser.add_argument('-p','--preferred', type=int)
    parser.add_argument('-r','--remove', action='store_true', default=False)
    args = parser.parse_args()

    # get gxl utility version strings
    cen_gen_vers = get_cen_gen_version()
    knn_gen_vers = get_knn_graph_gen_version()
    make_symmetric_vers = get_knn_make_symmetric_gen_version()
    make_index_vers = get_make_index_gen_version()

    # collect results for export later
    results = []

    # get leda card info
    num_boards, board_details = get_leda_info()
    print("\nFound %d boards" % num_boards)
    if num_boards==0:
        raise Exception("ERROR: Could not find any APU boards")
    print()
    results.append( {'operation':'ledainfo', 'subop':'boards', \
        'numboards': num_boards, 'board_details':str(board_details), \
        'cpunodebind':args.cpunodebind, 'preferred':args.preferred } )

    # get the current working dir to be reset later
    curdir = os.getcwd()

    # create a temp working dir
    tmpdir = tempfile.mkdtemp()
    os.chmod(tmpdir,0o777)
    print('Created temporary directory', tmpdir)

    # copy datasets locally
    retv = get_datasets( tmpdir, args.dataset )
    if not retv: cleanup(tmpdir, error=True, msg="ERROR: Could not copy datasets.")
    fbin_path, lbl_path = retv

    # run centroids generation
    s = datetime.now()
    if not run_cen_gen_utility( args.cpunodebind, args.preferred, tmpdir, fbin_path):
        cleanup(tmpdir, error=True, msg="ERROR: Could not generate centroids.")
    e = datetime.now()
    print("cen gen walltime=", (e-s).total_seconds())
    results.append( {'operation':'build-index', 'subop':'cen_gen', \
        'version':cen_gen_vers, 'start':s, 'end':e, 'walltime': (e-s).total_seconds(),\
        'cpunodebind':args.cpunodebind, 'preferred':args.preferred } )
 
    # run knn graph generation
    s = datetime.now()
    if not run_knn_graph_gen_utility( args.cpunodebind, args.preferred, tmpdir, fbin_path):
        cleanup(tmpdir, error=True, msg="ERROR: Could not generate knn graph.")
    e = datetime.now()
    print("knn gen walltime=", (e-s).total_seconds())
    results.append( {'operation':'build-index', 'subop':'knn_gen', \
        'version':knn_gen_vers, 'start':s, 'end':e, 'walltime': (e-s).total_seconds(), \
        'cpunodebind':args.cpunodebind, 'preferred':args.preferred } )
 
    # make knn graph symmetric
    s = datetime.now()
    if not run_knn_make_symmetric_gen_utility( args.cpunodebind, args.preferred, tmpdir ):
        cleanup(tmpdir, error=True, msg="ERROR: Could not make knn graph symmetric.")
    e = datetime.now()
    print("knn symmmetric walltime=", (e-s).total_seconds())
    results.append( {'operation':'build-index', 'subop':'knn_symmetric', \
        'version': make_symmetric_vers, 'start':s, 'end':e, 'walltime': (e-s).total_seconds(),\
        'cpunodebind':args.cpunodebind, 'preferred':args.preferred } )
    
    # make the index
    s = datetime.now()
    if not run_index_gen_utility( args.cpunodebind, args.preferred, tmpdir, fbin_path, lbl_path, args.m, args.e ):
        cleanup(tmpdir, error=True, msg="ERROR: Could not generate the index.")
    e = datetime.now()
    print("make index walltime=", (e-s).total_seconds())
    results.append( {'operation':'build-index', 'subop':'index_gen', \
        'version': make_index_vers, 'start':s, 'end':e, 'walltime': (e-s).total_seconds(), \
        'cpunodebind':args.cpunodebind, 'preferred':args.preferred } )

    # finalize
    os.chdir( curdir )
    if args.remove:
        remove_index(tmpdir, args.output)
    else:
        path = move_index(tmpdir, args.output)
        print("Generated index is at %s" % path)
    write_results(results, args.dataset, args.output )
    cleanup(tmpdir)
    print("Done.")

    sys.exit(0)
