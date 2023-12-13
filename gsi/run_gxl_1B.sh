#!/bin/bash

set -e
set -x

#
# setup and config
#

# get name of timestamped output dir
TIMESTAMP=$(date +%s)
OUTPUT="/tmp/gxl_$TIMESTAMP"

#
# Run GXL commands
#

# run GXL on 1B
DATASET="deep-1000M"
echo "Running GXL on $DATASET"
echo "Writing output to $OUTPUT"
python -u gxl_bench.py --dataset $DATASET --output $OUTPUT | tee "$OUTPUT/$DATASET.log"
