# Dagens Nyheter

The curation and analysis of Dagens Nyheter corpus

### scripts/ 

Scripts to download json files segment various sections into xml-standard EPUB.

* `download_dn.py`: this script searches inside the Kblab API and fetches all dn-files associated with a specified time period.
* `process_to_epub.py`: this script segments and processes the files and outputs Epub files.

### quality-control/ 

This directory contains the quality control of two dimensions within the curation of the corpus: namely the quality of the segmentation of articles in dagens-nyheter, found inside `article-segmentation/` and that of the OCR quality, found inside `ocr-estimation/`.

### topic-modelling/

This directory contains the scripts to run a full topic modelling pipeline with Latent Dirichlet Allocation (LDA) on processed dagens nyheter corpus.

