#!/bin/sh
# Shell script to get westac hub files from epubs

# get input.txt and documents.csv from epubs
python3 scripts/generate_inputs.py

# preprocess input.txt
python3 scripts/preprocess_input.py

# run pclda topic model on inputs.py to generate z_files
java -cp /Users/liamtabibzadeh/Documents/jobb/PartiallyCollapsedLDA/target/PCPLDA-9.2.2.jar cc.mallet.topics.tui.ParallelLDA --run_cfg=input.txt

# move relevant z files into z_files dir
python3 scripts/exctract_z_files.py

# run humlabs pipeline on z_files
python3 /Users/liamtabibzadeh/Documents/jobb/PCLDA-pipeline/pclda_pipeline/convert.py z_files/*.csv --target-folder=westac_hub_files
