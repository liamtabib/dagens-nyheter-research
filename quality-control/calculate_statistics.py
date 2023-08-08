import pathlib as path

def find_

from lxml import etree
import pandas as pd
from pathlib import Path
from scipy.stats import beta
import argparse

XML_NS = "{http://www.w3.org/XML/1998/namespace}"

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