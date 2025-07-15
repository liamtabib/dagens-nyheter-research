import pathlib as path
from lxml import etree
import pandas as pd
from pathlib import Path
import numpy as np
import argparse
import nltk
import json
import xml.etree.ElementTree as ET


def iterator_json(df):
    edit_distances = []

    for index, row in df.iterrows():
        edition_id = row['edition_id']
        true_content = row['content']
        
        json_dir_path = Path('../dn-extra/files/raw_json/')
        path_json_editions = json_dir_path.rglob(f'{edition_id}_content.json')
        for x in path_json_editions:
            with x.open('r', encoding='utf-8') as f:
                correct_json_ed = json.load(f)

        for block in correct_json_ed:
            if block['@id'] == row['facs']:
                tesseract_content = block['content']
                edit_distances.append(nltk.edit_distance(true_content,tesseract_content))
                break

    print(f'average edit_distance for tesseract: {np.mean(edit_distances)}')


def iterator_xml(df):
    edit_distances = []

    xmlns='http://www.loc.gov/standards/alto/ns-v2#'

    for index, row in df.iterrows():
            true_content = row['content']
            edition_id = row['edition_id']
            page_number = row['facs'].split("#")[1][2]

            xml_dir_path = Path('../dn-extra/files/raw_xml/')
            num_zeros= '0'*(4-len(page_number))
            xml_filename = edition_id + '_' + num_zeros + page_number + '.xml'
            path_page = xml_dir_path.rglob(xml_filename)

            for p in path_page:
                minimum_d = 1000

                tree = ET.ElementTree(etree.parse(p))
                for block in tree.iterfind('.//{%s}TextBlock' % xmlns):
                    block_content = []

                    for lines in block.iterfind('.//{%s}TextLine' % xmlns):

                        # Loop over all words in <TextLine>, find all child elements <String> 
                        for word in lines.findall('{%s}String' % xmlns):

                            if 'SUBS_TYPE' in word.attrib:

                                if 'HypPart1' in word.attrib.get('SUBS_TYPE'):
                                    fetch_word = word.attrib.get('SUBS_CONTENT')
                                else:
                                    fetch_word = ''
                            else:
                                fetch_word = word.attrib.get('CONTENT')

                            block_content.append(fetch_word)

                    block_content = ' '.join(block_content)

                    edit_d = nltk.edit_distance(true_content,block_content)
                    if edit_d < minimum_d:
                        minimum_d = edit_d

                edit_distances.append(minimum_d)
    print(f'average edit_distance for xyz: {np.mean(edit_distances)}')

def main(args):
    df=pd.read_csv(args.path_goldstandard,sep=';')
    print(df.columns)
    iterator_xml(df)
    iterator_json(df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path_goldstandard", type=str, default = 'validation/ocr_validation/annotations/sample.csv')
    args = parser.parse_args()
    main(args)

