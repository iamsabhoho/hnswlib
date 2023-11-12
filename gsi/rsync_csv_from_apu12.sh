#!/bin/bash

mkdir -p data

rsync -avh gwilliams@192.168.99.33:/home/gwilliams/Projects/GXL/hnswlib/gsi/data/*.csv ./data/
