#!/bin/bash

mkdir -p data

rsync -avh gwilliams@192.168.99.33:/mnt/nas1/GXL/deep1B/v1.2/*.csv ./data/
