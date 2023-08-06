The curation and analysis of Dagens Nyheter corpus:

/scripts: Scripts to download and segment the raw json files into xhtml
download_dn.py: this script searches inside kblab betalab API and downloads all files associated with all available utgåvor.
process_to_epub.py: this script processes the downloaded files and returns epubs.

/quality-control: Annotation of gold standard set for quality-control of segmentation of articles

/topic-modelling: performs topic model on articles
