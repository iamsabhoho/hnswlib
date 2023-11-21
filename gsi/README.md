
GXL Benchmarking Tools

This directory contains GXL benchmark tools and analysis:
* gxl_bench.py - This will run all the GLX utilities on a chosen dataset (ie, "deep-10M")  and will export the index and timing related CSV data to the directory you specify.
* np_convert_to_fbin.py - This will convert a numpy dataset to the format expected by GXL (see GXL wiki for more details.)
* gen_labels.py - This will create a trivial numeric labels dataset required by the GXL utilities. 
* rsync_csv_from_nas1.sh - This is a helper script to sync just the CSV files from a benchmkark machine.
* analyze_gxl_benchmkars.ipynb - This is a notebook to analyze just the GXL build benchmarks.
 

