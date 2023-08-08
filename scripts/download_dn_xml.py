from kblab import Archive
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path
import multiprocessing
import json
import argparse
import os
import xml.etree.ElementTree as ET

def get_ids(pw,n_editions):
    """returns all IDs of the matches in the betalab API for the 'Dagens nyheter' search'"""
    a = Archive('https://betalab.kb.se', auth=("demo", pw))
    ids = []
    for package_id in a.search({'label': 'DAGENS NYHETER'},max=n_editions):
        ids.append(package_id)
    return ids


def store_files(package_id, pw, p):
    """ Reads an id of a specific edition and stores content files, metadata files, and structure files.
    """
    a = Archive("https://betalab.kb.se", auth=("demo", pw))

    try:
        meta = requests.get(f"https://betalab.kb.se/{package_id}/meta.json", auth=HTTPBasicAuth("demo", pw))
        meta = json.loads(meta.text)
        year=meta['year']

        year_path= p / year

        if os.path.exists(year_path):
            pass
        else:
            os.makedirs(year_path)
        edition_path = year_path / package_id

        if os.path.exists(edition_path):
            pass
        else:
            os.makedirs(edition_path)
            
        for x in a.get(package_id):
                
                if "alto.xml" in x:
                    page=requests.get(f"https://betalab.kb.se/{package_id}/{x}", auth=HTTPBasicAuth("demo", pw),stream=True)
                    if page.status_code == 200:
                        tree= ET.ElementTree(ET.fromstring(page.text))
                        page_name = x.split("_")
                        page_number = page_name[-2]
                        file_name_xml = package_id + f'_{page_number}.xml'
                        filepath_xml= edition_path / file_name_xml
                        #Download the file

                        tree.write(filepath_xml)

    except Exception as e:
        print(f"Error occurred for package ID: {package_id} - {str(e)}")


def count_files():
    years=list(Path('corpus/raw_xml/').glob('*'))
    n_files_=0
    d={}
    for year in years:
        n_editions=len(list(Path(year).glob('*')))
        n_files_+=n_editions
        d[int(year.name)]=n_editions
    for year, n_files in sorted(d.items()):
        print(f'{year} has {n_files} editions')
    
    print(f'there are {n_files_} editions inside raw_xml directory')



def main(args):
    p = Path("corpus/raw_xml/")
    p.mkdir(parents=True, exist_ok=True)
    with open(args.path_kb_cred, 'r') as file:
        pw = file.read().replace('\n', '')
    
    ids = get_ids(pw,args.number_of_editions)
    try:
        with multiprocessing.Pool() as pool:
            pool.starmap(store_files, [(package_id, pw, p) for package_id in ids])
    except Exception as e:
        print(str(e))
    
    count_files()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path_kb_cred", type=str, default="/Users/liamtabibzadeh/Documents/jobb/kb_credentials.txt")
    parser.add_argument("--number_of_editions", type=str, default=80)
    args = parser.parse_args()
    main(args)
