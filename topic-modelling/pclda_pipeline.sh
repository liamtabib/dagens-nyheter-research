#!/bin/sh
# reads in epubs in a pipeline and outputs topic model bundle

BASE_DIR=~/Documents/jobb

cd "$BASE_DIR/dagens_nyheter"

# get input.txt and documents.csv from epubs
python3 topic_modelling/scripts/generate_inputs.py

echo Generating input.txt and documents.zip from topic_modelling/scripts/generate_inputs.py 

[ -s topic_modelling/input.txt ] && echo "input.txt exists and is not empty" || \
{ echo "input.txt from generate_inputs.py does not exist or is empty."; exit 1; }

# preprocess input.txt
python3 topic_modelling/scripts/preprocess.py

echo Generating input_clean.txt from topic_modelling/scripts/preprocess.py 

[ -s topic_modelling/input_clean.txt ]  && echo "input_clean.txt exists and is not empty" || \
{ echo "input_clean.txt from preprocess.py does not exist or is empty."; exit 1; }

rm topic_modelling/input.txt && echo "input.txt deleted" 

#check if there exists already a config file and input_clean.txt in PartiallyCollapsedLDA root.
rm -rf "$BASE_DIR/PartiallyCollapsedLDA/input_clean.txt" 
rm -rf "$BASE_DIR/PartiallyCollapsedLDA/dn_config.cfg" 

cp topic_modelling/dn_config.cfg "$BASE_DIR/PartiallyCollapsedLDA"
cp topic_modelling/input_clean.txt "$BASE_DIR/PartiallyCollapsedLDA"

#move to run model
cd "$BASE_DIR/PartiallyCollapsedLDA"

# run pclda topic model on inputs.py to generate z_files
java -cp target/PCPLDA-9.2.2.jar cc.mallet.topics.tui.ParallelLDA --run_cfg=dn_config.cfg

if [ -z "$(ls -A $BASE_DIR/PartiallyCollapsedLDA/Runs)" ]; then
  echo "Runs dir is empty"
  exit 1
fi

cd "$BASE_DIR/dagens_nyheter/"

# move relevant z files into z_files dir
python3 topic_modelling/scripts/pick_z_files.py --path_pclda_runs="$BASE_DIR/PartiallyCollapsedLDA/Runs"

# run humlabs pipeline on z_files
python3 "$BASE_DIR//PCLDA-pipeline/pclda_pipeline/convert.py" topic_modelling/z_files/*.csv --target-folder=topic_modelling/westac_hub_files

cd topic_modelling
# test to unzip and check content
mkdir temp_for_zip_extract
unzip westac_hub_files/\*.zip -d temp_for_zip_extract
ls temp_for_zip_extract

cd temp_for_zip_extract

shopt -s nullglob # Ensure that an empty glob expands to nothing instead of the literal "*"
for file in *; do
  echo "$file"
  [ -s "$file" ] || { echo "$file does not exist or is empty."; exit 1; }
done

rm -r ../temp_for_zip_extract
