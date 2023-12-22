
# GXL Python Benchmarking Tools

## Prerequisites

* python >= 3.8 (We used Anaconda to create the proper environment)
* install packages via [requirements.txt](requirements.txt)

## How We Benchmark Building Indexes With GXL

We created [gxl_bench.py](gxl_bench.py) which invokes the various GXL utilities with timing and exports a CSV with the timing data.

Please consult the script [run_gxl_apu3.sh](run_gxl_apu3.sh)  which demonstrates how we invoked the python file for various subsets of deep-1B.

Note that you might need to adjust the python file to reflect your environment (ie, where the fbin and lbl files are located, etc.)

## How We Benchmark Searching On GXL Indexes

We created [gxl.py](gxl.py) which loads GXL indexes and run it through hnswlib knn search. 

This script shows an example of loading a GXL-built index for Deep1B-1000M. Please note the file paths and parameters use and change them as needed.

## How We Benchmark Building And Searching With HNSWLIB

We created [vanilla.py](vanilla.py) which creates and searches with [hnswlib](https://github.com/nmslib/hnswlib/tree/master). 

This script shows an example of building and searching HNSWLIB-built index for Deep1B-1000M. Please note the file paths and parameters use and change them as needed.

## Visualizing the Benchmark Data

Please consult the jupyter notebook [analyze.ipynb](analyze.ipynb).

## TODO

* python files "hard-code" various parameters and directories such as paths to the fbin/lbl datasets and location of GXL utilites, so we should make those changeable via command line arguments
* graphs which focus on 100M or higher should use "hours" on y axis
* gxl_bench.py should be able to predict the amount of disk storage needed and warn user if its too low
* gxl_bench.py should report on the properties of the disk used (ie, nvm or not)
 

