#!/bin/bash

set -e
set -x

#
# setup and config
#

# create timestamped output dir
TIMESTAMP=$(date +%s) # form a top-level directory name with current timestamp
OUTPUT="/mnt/nvme1/george/GXL/experiments/gxl_$TIMESTAMP"
mkdir -p $OUTPUT

#
# Run GXL commands
#

# run GXL on 1M
DATASET="deep-1M"
echo "Running GXL on $DATASET"
echo "Writing output to $OUTPUT"
python -u gxl_bench.py --dataset $DATASET --output "$OUTPUT/$DATASET" | tee "$OUTPUT/$DATASET.log" 

# run GXL on 10M
DATASET="deep-10M"
echo "Running GXL on $DATASET"
echo "Writing output to $OUTPUT"
python -u gxl_bench.py --dataset $DATASET --output "$OUTPUT/$DATASET"  | tee "$OUTPUT/$DATASET.log"

# run GXL on 20M
DATASET="deep-20M"
echo "Running GXL on $DATASET"
echo "Writing output to $OUTPUT"
python -u gxl_bench.py --dataset $DATASET --output "$OUTPUT/$DATASET"  | tee "$OUTPUT/$DATASET.log"

# run GXL on 50M
DATASET="deep-50M"
echo "Running GXL on $DATASET"
echo "Writing output to $OUTPUT"
python -u gxl_bench.py --dataset $DATASET --output "$OUTPUT/$DATASET" | tee "$OUTPUT/$DATASET.log"

# run GXL on 100M
DATASET="deep-100M"
echo "Running GXL on $DATASET"
echo "Writing output to $OUTPUT"
python -u gxl_bench.py --dataset $DATASET --output "$OUTPUT/$DATASET" | tee "$OUTPUT/$DATASET.log"

# run GXL on 250M
DATASET="deep-250M" 
echo "Running GXL on $DATASET"
echo "Writing output to $OUTPUT"
python -u gxl_bench.py --dataset $DATASET --output "$OUTPUT/$DATASET"  | tee "$OUTPUT/$DATASET.log"

