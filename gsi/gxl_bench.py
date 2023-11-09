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
CEN_GEN    =   "run-gxl-cen-gen"

# set to True for debugging
VERBOSE     = True

#
# imports
#
import os
import argparse
import time
from subprocess import Popen, PIPE, STDOUT
import tempfile

def get_leda_info( ):
    '''Get LedaG card info.'''

    slots = []

    #
    # This is gnarly code to invoke the ledagssh command,
    # capture the output, detect the prompt, and send it
    # the quit command.
    #
    cmd = LEDAGSSH.split()
    if VERBOSE: print("running leda command", cmd )
    p = Popen( cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT) 
    os.set_blocking(p.stdout.fileno(), False)
    while True:
        if p.returncode!=None:
            if VERBOSE: print("leda command terminated.")
            break
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

def run_cen_gen_utility( fbin ):
    '''Runs the GXL centroids generation utility.'''

    cmd = [ os.path.join( GXL_PATH, CEN_GEN ),  ]
    cmd += [ fbin ]
    if VERBOSE: print("running gxl command", cmd )

    p = Popen( cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=False)
    os.set_blocking(p.stdout.fileno(), False)
    while True:
        if p.returncode!=None:
            if VERBOSE: print("gxl command terminated.")
            break
        b = p.stdout.readline()
        if b==b'':
            time.sleep(0.01)
            p.stdout.flush()
            continue
        bs = b.decode('utf-8')
        if VERBOSE:
            print("gxl: %s" % bs, end="")
        #if bs.find("CENTROIDS GENERATION TIME")>=0:
        #    p.terminate()
        #    p.communicate() # process won't terminate without this

    return True

if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser("gxl benchmarking tool.")
    parser.add_argument('-u','--gxl_utilities_path',  default=GXL_PATH)
    parser.add_argument('-n','--npy_path', default=DSET_PATH)
    args = vars(parser.parse_args())

    # get leda card info
    num_boards, board_details = get_leda_info()
    print("Found %d boards" % num_boards)
    if num_boards==0:
        raise Exception("Could not find any APU boards")

    run_cen_gen_utility( "/home/gwilliams/Projects/GXL/deep-10M.fbin" )



