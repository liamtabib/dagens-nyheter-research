from kblab import Archive
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path
import multiprocessing
import json
import argparse

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
    try:
        meta = requests.get(f"https://betalab.kb.se/{package_id}/meta.json", auth=HTTPBasicAuth("demo", pw))
        meta = json.loads(meta.text)

        content = requests.get(f"https://betalab.kb.se/{package_id}/content.json", auth=HTTPBasicAuth("demo", pw))
        content = json.loads(content.text)

        stucture = requests.get(f"https://betalab.kb.se/{package_id}/structure.json", auth=HTTPBasicAuth("demo", pw))
        structure = json.loads(stucture.text)

        file_name_meta = package_id + '_meta.json'
        file_name_content = package_id + '_content.json'
        file_name_structure = package_id + '_structure.json'

        filepath_meta = p / file_name_meta
        filepath_content = p / file_name_content
        filepath_structure = p / file_name_structure

        with filepath_meta.open("w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        with filepath_content.open("w", encoding="utf-8") as f:
            json.dump(content, f, indent=2)

        with filepath_structure.open("w", encoding="utf-8") as f:
            json.dump(structure, f, indent=2)

    except Exception as e:
        print(f"Error occurred for package ID: {package_id} - {str(e)}")

def main(args):
    p = Path("corpus/json_Dagens_nyheter/")
    p.mkdir(parents=True, exist_ok=True)
    with open(args.path_kb_cred, 'r') as file:
        pw = file.read().replace('\n', '')
    
    ids = get_ids(pw,args.number_of_editions)
    try:
        with multiprocessing.Pool() as pool:
            pool.starmap(store_files, [(package_id, pw, p) for package_id in ids])
            print(f'sucessfully downloaded {len(ids)} editions')
    except Exception as e:
        print(str(e))
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path_kb_cred", type=str, default="/Users/liamtabibzadeh/Documents/jobb/kb_credentials.txt")
    parser.add_argument("--number_of_editions", type=str, default=80)
    args = parser.parse_args()
    main(args)
