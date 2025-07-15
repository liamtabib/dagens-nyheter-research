import argparse
import pathlib as path
from pathlib import Path

import pandas as pd
from lxml import etree
from scipy.stats import beta

XML_NS = "{http://www.w3.org/XML/1998/namespace}"


def elem_iter(root):
    """Iterator over XML elements returning (tag, element) tuples."""
    for elem in root.iter():
        yield elem.tag, elem


def edition_iterators(corpus_path, start=1867, end=2022):
    """Iterator over edition files in the corpus directory within date range."""
    corpus_path = Path(corpus_path)
    if not corpus_path.exists():
        return
    
    for edition_file in corpus_path.rglob("*.xml"):
        # Extract year from filename or path if possible
        yield edition_file


def infer_metadata(filepath):
    """Infer metadata from filepath."""
    path = Path(filepath)
    # Basic metadata extraction from filename/path
    return {
        "year": "unknown",
        "chamber": "unknown"
    }

def estimate_accuracy(edition, df):
    
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.parse(edition, parser).getroot()

    correct, incorrect = 0, 0
    ids = set(df["elem_id"])

    found_correct_element=False

    for tag, elem in elem_iter(root):

        if found_correct_element and 'who' in elem.attrib:

            predicted_wiki_id = elem.attrib.get('who', None)

            if predicted_wiki_id==actual_wiki_id:
                correct+=1
            else:
                incorrect+=1
            #reset boolean
            found_correct_element=False
        
                
        if tag == "note" and found_correct_element==False:
            x = elem.attrib.get(f'{XML_NS}id', None)
            if x in ids:
                actual_wiki_id = df[df["elem_id"] == x]["speaker_wiki_id"].iloc[0]
                found_correct_element=True

    return correct, incorrect


def main(args):
    editions = list(edition_iterators("corpus/", start=args.start, end=args.end))
    df=pd.read_csv(args.path_goldstandard)

    rows = []
    correct, incorrect = 0, 0
    for p in editions:
        path = Path(p)
        edition_id = path.stem
        
        #print(p, edition_id)
        df_p = df[df["edition_id"] == edition_id]
        if len(df_p) >= 1:

            acc = estimate_accuracy(path, df_p)
            metadata=infer_metadata(p)
            
            correct += acc[0]
            incorrect += acc[1]

            if acc[1] + acc[0] > 0:
                rows.append([acc[0], acc[1], acc[0] / (acc[0] + acc[1]), metadata["year"], metadata["chamber"]])
    accuracy = correct / (correct + incorrect)





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=1867)
    parser.add_argument("--end", type=int, default=2022)
    parser.add_argument("--path_goldstandard", type=str, required=True)
    args = parser.parse_args()
    df = main(args)

    print(df)