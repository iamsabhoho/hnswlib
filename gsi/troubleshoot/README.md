
This directory contains info and files to reproduce/troubleshoot the GXL vs vanilla built HNSWLib indexes.

Files:
* deep-100M.txt - the results of our test on Deep1B (100M subset)
* requirements.txt - please install these python packages via pip
* test.py - please run this python program to reproduce our results

Important:
* We tested with Python 3.8 provided by a conda environment.
* You should run this on apu12 at 99.33a
* There are various settings you can change in test.py
