import xml.etree.ElementTree as ET
from pathlib import Path
from ebooklib import epub
from lxml import etree
import numpy as np
import json


def main():
    xml_dir_path = Path('corpus/raw_xml/')
    path_xml_editions = list(xml_dir_path.glob('*/*'))
    xmlns='http://www.loc.gov/standards/alto/ns-v2#'
    blocks_xml_editions=[]

    for path_edition in path_xml_editions:
        xml_paths = list(Path(path_edition).glob('*'))
        blocks_in_single_edition=0

        for xml_path in xml_paths:

            tree = ET.ElementTree(etree.parse(xml_path))
            for block in tree.iterfind('.//{%s}TextBlock' % xmlns):
                blocks_in_single_edition += 1
        blocks_xml_editions.append(blocks_in_single_edition)
    
    print('----------')

    json_dir_path = Path('corpus/json_Dagens_nyheter/')
    path_json_editions = list(json_dir_path.rglob('*_content.json'))
    blocks_json_editions=[]
    
    for path_edition in path_json_editions:
        n_text_blocks = 0
        with path_edition.open('r', encoding='utf-8') as f:
            raw_content_json = json.load(f)
            for x in raw_content_json:
                if x['@type'] == 'Text':
                    n_text_blocks += 1
            blocks_json_editions.append(n_text_blocks)

    for x in range(0,80):
        print(blocks_json_editions[x],blocks_xml_editions[x])

    



                


    



if __name__ == '__main__':
    main()