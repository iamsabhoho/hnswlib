
GXL Benchmarking Tools

# Prerequisites

* python >= 3.8 (We used Anaconda to create the proper environment)
* install packages via requirements.txt 

# How We Benchmark the GXL

We created [gxl_bench.py](gxl_bench.py) which invokes the various GXL utilities with timing and exports a CSV with the timing data.

Please consult the script [run_gxl_apu3.sh](run_gxl_apu3.sh)  which demonstrates how we invoked the python file for various subsets of deep-1B.

Note that you might need to adjust the python file to reflect your environment (ie, where the fbin and lbl files are located, etc.)

# Visualizing the Benchmark Data

Please consult the jupyter notebook [analyze.ipynb](analyze.ipynb).
 

