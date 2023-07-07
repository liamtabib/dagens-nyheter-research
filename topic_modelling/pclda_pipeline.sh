#!/bin/sh
# Shell script to get westac hub files from epubs

BASE_DIR=~/Documents/jobb

# get input.txt and documents.csv from epubs
python3 topic_modelling/scripts/generate_inputs.py

# preprocess input.txt
python3 topic_modelling/scripts/preprocess.py

cp topic_modelling/pclda_input/* "$BASE_DIR/PartiallyCollapsedLDA/"

#move to run model
cd "$BASE_DIR/PartiallyCollapsedLDA/"

# run pclda topic model on inputs.py to generate z_files
java -cp target/PCPLDA-9.2.2.jar cc.mallet.topics.tui.ParallelLDA --run_cfg=dn_config.cfg

if [ -z "$(ls -A Runs)" ]; then
   echo 'Runs dir is empty'
   exit 1
fi

cd "$BASE_DIR/dagens_nyheter/"

# move relevant z files into z_files dir
python3 topic_modelling/scripts/pick_z_files.py

# run humlabs pipeline on z_files
python3 "$BASE_DIR//PCLDA-pipeline/pclda_pipeline/convert.py" topic_modelling/z_files/*.csv --target-folder=topic_modelling/westac_hub_files