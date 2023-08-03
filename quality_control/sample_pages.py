import pandas as pd
from lxml import etree
from pathlib import Path
import json
def sample_editions():
    pass

def sample_pages():
    pass

def main():
    pass


def read_year(identifier):
    """ reads in an id dagens nyheter edition, returns the creation year """
    pathlist = Path('corpus/json_Dagens_nyheter/').glob(f'{identifier}_meta.json')
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


if __name__ == "__main__":
    protocol_df = get_page_counts()
    print(protocol_df)

