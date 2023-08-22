import numpy as np
import pandas as pd
from lxml import etree
from pathlib import Path
import json
import argparse,hashlib
import os, sys

def sample_pages(df, random_state=None):
    pages = np.array(df["pages"])
    x = np.random.randint(np.zeros(len(pages)), pages)
    if random_state is not None:
        x = random_state.randint(np.zeros(len(pages)), pages)
    df["x"] = x

    parser = etree.XMLParser(remove_blank_text=True)
    rows = []
    for _, row in df.iterrows():
        edition_path = row["edition_path"]
        x = row["x"]
        root = etree.parse(edition_path, parser)
        pbs = root.findall(".//{http://www.w3.org/1999/xhtml}pb")
        facs = pbs[x].attrib["facs"]
        rows.append([row['edition_id'], facs,''])

    df = pd.DataFrame(rows, columns=["edition_id", "facs",'start_article'])

    return df

def sample_page_counts(df, start, end, n, seed=None):
    df = df[df["year"] >= start]
    df = df[df["year"] <= end].copy()
    df["p"] = df["pages"] / df["pages"].sum()
    if df.empty:
        pass
    else:
        sample = df.sample(n, weights="p", replace=True, random_state=seed)
        #sample = sample.groupby(['protocol_id'], as_index=False).size()

        return sample

def read_year(identifier):
    """ reads in an id dagens nyheter edition, returns the creation year """
    pathlist = Path('files/raw_json/').glob(f'{identifier}_meta.json')
    for path in pathlist:
        with path.open('r', encoding='utf-8') as f:

                raw_metadata = json.load(f)

                return raw_metadata['year']


def get_page_counts():
    pathlist = Path('corpus/epubs/').rglob('content.xhtml')
    parser = etree.XMLParser(remove_blank_text=True)
    rows = []
    for edition_path in pathlist:
        edition_id=edition_path.parent.parent.stem
        year = read_year(edition_id)
        root = etree.parse(edition_path, parser)
        pbs = root.findall(".//{http://www.w3.org/1999/xhtml}pb")
        rows.append([edition_path, edition_id, int(year), len(pbs)])

    df = pd.DataFrame(rows, columns=["edition_path", "edition_id", "year", "pages"])
    return df


def main(args):
    digest = hashlib.md5(args.seed.encode("utf-8")).digest()
    digest = int.from_bytes(digest, "big") % (2**32)

    edition_df = get_page_counts()

    try:
        to_annotate_dir='quality-control/to_annotate'
        os.makedirs(to_annotate_dir)
    except FileExistsError:
        print('this script has already been run and annotations are started')
        print('The decades in the to_annotate directory are:')
    
        file_names=list(Path(to_annotate_dir).glob('*.csv'))
        
        for file_name in file_names:
            decade = str(file_name)[-8:-4]
            print(decade,end=' ')
        sys.exit()

    for decade in range(args.start // 10 * 10, args.end, 10):
        print("Decade:", decade)
        sample = sample_page_counts(edition_df, decade, decade + 9, n=args.pages_per_decade, seed=digest)
        if isinstance(sample, pd.DataFrame):
            prng = np.random.RandomState( (digest+decade) % (2**32))
            sample = sample_pages(sample, random_state=prng)
            sample = sample.sort_values(["edition_id"])
            sample.to_csv(f"{to_annotate_dir}/sample_{decade}.csv", index=False)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-f", '--seed', type=str, default=None, help="Random state seed")
    parser.add_argument('-p', '--pages_per_decade', type=int, default=3, help="How many pages per decade? 3")
    parser.add_argument("-s", "--start", type=int, default=1890, help="Start year")
    parser.add_argument("-e", "--end", type=int, default=2022, help="End year")
    args = parser.parse_args()
    main(args)