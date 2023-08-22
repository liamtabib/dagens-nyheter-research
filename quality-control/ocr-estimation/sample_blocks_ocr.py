import numpy as np
import pandas as pd
from lxml import etree
from pathlib import Path
import json
import argparse,hashlib
import os, sys
import random


def sample_blocks(seed):

    json_dir_path = Path('../dn-extra/files/raw_json/')
    content_file_paths = list(json_dir_path.rglob('*_content.json'))
    rows = []
    random.seed(seed)
    for content_path in random.sample(content_file_paths,4):

        with content_path.open('r', encoding='utf-8') as f:
            raw_file = json.load(f)
        
        #get the general shape of the page link
        identifier=content_path.stem.split('_')[0]

        text_blocks = []

        for json_block in raw_file:
            if json_block['@type'] == 'Text':
                text_blocks.append(json_block)
        
        sampled_block = random.sample(text_blocks,1)[0]
        link = sampled_block['@id']
        print(link)

        rows.append([identifier, link,''])

    df = pd.DataFrame(rows, columns=["edition_id","facs",'content'])
    return df


def main(args):
    digest = hashlib.md5(args.seed.encode("utf-8")).digest()
    digest = int.from_bytes(digest, "big") % (2**32)

    try:
        to_annotate_dir='quality-control/ocr-estimation/to-annotate' #CHANGE THIS
        os.makedirs(to_annotate_dir)
    except FileExistsError:
        print('this script has already been run and annotations are started')
        sys.exit()

    sample = sample_blocks(seed=digest)
    
    sample = sample.sort_values(["edition_id"])
    sample.to_csv(f"{to_annotate_dir}/sample.csv", index=False)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-f", '--seed', type=str, default=1, help="Random state seed")
    args = parser.parse_args()
    main(args)