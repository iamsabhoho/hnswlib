#!/bin/bash

set -e
set -x

#
# setup and config
#

# create timestamped output dir
TIMESTAMP="1702496880" #$(date +%s)
OUTPUT="/mnt/nvme1/george/GXL/experiments/gxl_$TIMESTAMP"
#mkdir -p $OUTPUT

#
# Run GXL commands
#

# run GXL on 500M
DATASET="deep-500M"
echo "Running GXL on $DATASET"
echo "Writing output to $OUTPUT"
python gxl_bench.py --dataset $DATASET --output "$OUTPUT/$DATASET" | tee "$OUTPUT/$DATASET.log"
