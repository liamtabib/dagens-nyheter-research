# historical-docs-processor

The curation and analysis of Dagens Nyheter corpus for historical newspaper research.

## Setup

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

### src/

Core document processing pipeline for JSON to EPUB conversion.

* `json_to_epub_converter.py`: Main converter - segments and processes JSON content files into structured EPUB files
* `xml_to_epub_converter.py`: XML processing variant for alternative input formats
* `summary_statistics.py`: Generates corpus statistics and analytics
* `test_textline_mapping.py`: Tests text line mapping functionality
* `update_tesseract.py`: Updates Tesseract OCR configuration

**Usage:**
```bash
python src/json_to_epub_converter.py
```

### validation/

Quality assurance framework for corpus validation and integrity checking.

#### segmentation/
- `segmentation_validator.py`: Evaluates article segmentation accuracy using statistical metrics
- `segmentation_sampler.py`: Samples pages for segmentation testing and annotation
- `annotations/`: Contains annotated datasets for validation
- `to_annotate/`: Staging area for annotation workflows

#### ocr_validation/
- `ocr_validator.py`: Estimates OCR quality metrics and accuracy scores
- `ocr_sampler.py`: Samples text blocks for OCR quality analysis
- `annotations/`: Contains OCR quality annotations and ground truth data

### tests/

Integration tests to verify end-to-end functionality and data integrity.

**Usage:**
```bash
python tests/integration_tests.py
```

### transforms/

Data transformation pipeline with topic modeling capabilities.

**Processing Pipeline:**
1. `batch_generator.py`: Generates input batches from curated EPUB corpus
2. `text_preprocessor.py`: Cleans and preprocesses text data for analysis
3. `csv_combiner.py`: Merges multiple CSV input files
4. `file_selector.py`: Selects specific files for processing
5. `pclda_pipeline.sh`: Runs complete PCLDA topic modeling pipeline

**Usage:**
```bash
cd transforms
python scripts/text_preprocessor.py --input_path input.txt
bash pclda_pipeline.sh
```

## Dependencies

This project depends on external repositories:
- `PCLDA_pipeline`: Required for topic modeling pipeline
- `PartiallyCollapsedLDA`: LDA implementation

Ensure these are available as sibling directories to this project.

## Data Structure

Expected directory structure:
```
corpus/
├── editions/           # Processed EPUB editions
├── epubs_json/        # JSON-processed EPUBs
└── metadata/          # Corpus metadata files

files/
└── raw_json/          # Raw JSON content files from OCR

src/                   # Core processing pipeline
validation/            # Quality assurance framework
├── segmentation/      # Article segmentation validation
└── ocr_validation/    # OCR quality validation
transforms/            # Data transformation pipeline
└── scripts/          # Text processing scripts
tests/                 # Integration tests
```

