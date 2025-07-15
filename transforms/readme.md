Pipeline for topic model with dagens nyheter news:

1. batch_generator.py: based on the curated epubs of dagens nyheter, this script generates an input.txt file to be used as input to PCLDA model, and documents.csv to be used for the exploration of topic model.

2. text_preprocessor.py: preprocesses the input.txt by cleaning the text, returning input_clean.txt to be used as input PCLDA pipeline.

3. pclda_pipeline.sh: runs the pipeline from start to finish, including the above two scripts, the PCLDA model, the output of the model, and outputs the bundle in the directory 'westac_hub_files'. OBS! requires the repositories PCLDA_pipeline and  PartiallyCollapsedLDA as siblings of dagens_nyheter.