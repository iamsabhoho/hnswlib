#!/bin/bash

set -e
set -x

#
# setup and config
#

# create timestamped output dir
TIMESTAMP="1702496880" # Note we are wwriting into an existing directory with pre-determined timestamp
OUTPUT="/mnt/nvme1/george/GXL/experiments/gxl_$TIMESTAMP"

#
# Run GXL commands
#

# run GXL on 500M
DATASET="deep-500M"
echo "Running GXL on $DATASET"
echo "Writing output to $OUTPUT"
python -u gxl_bench.py --dataset $DATASET --output "$OUTPUT/$DATASET" | tee "$OUTPUT/$DATASET.log"
