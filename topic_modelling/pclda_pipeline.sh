#!/bin/sh
# Shell script to get westac hub files from epubs

# get input.txt and documents.csv from epubs
python3 topic_modelling/scripts/generate_inputs.py

# preprocess input.txt
python3 topic_modelling/scripts/preprocess.py

cp topic_modelling/pclda_input/* /Users/liamtabibzadeh/Documents/jobb/PartiallyCollapsedLDA/

if [ -z "$(ls -A ~/Documents/jobb/PartiallyCollapsedLDA/Runs)" ]; then
   echo 'Runs dir is empty'
   exit 1
fi

#move to run model
cd /Users/liamtabibzadeh/Documents/jobb/PartiallyCollapsedLDA/

# run pclda topic model on inputs.py to generate z_files
java -cp target/PCPLDA-9.2.2.jar cc.mallet.topics.tui.ParallelLDA --run_cfg=dn_config.cfg

#move back
cd /Users/liamtabibzadeh/Documents/jobb/dagens_nyheter/

# move relevant z files into z_files dir
python3 topic_modelling/scripts/pick_z_files.py

# run humlabs pipeline on z_files
python3 /Users/liamtabibzadeh/Documents/jobb/PCLDA-pipeline/pclda_pipeline/convert.py topic_modelling/z_files/*.csv --target-folder=topic_modelling/westac_hub_files