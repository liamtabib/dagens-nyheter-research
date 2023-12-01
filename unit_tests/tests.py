import pathlib
import shutil
from ebooklib import epub
from requests.auth import HTTPBasicAuth
import pandas as pd
from bs4 import BeautifulSoup
import requests
from pathlib import Path


# Test to check that all files in the Corpus can be read as epubs
def unittest_epub():
    path = pathlib.Path("corpus/editions")
    blms = [x for x in path.iterdir()]
    for x in blms:
        epub_name = x.name.replace("dn", "epub")
        epub_path = pathlib.Path("unittest_epub") / epub_name
        success = True
        if not epub_path.parent.exists():
            epub_path.parent.mkdir()
        try:
            shutil.make_archive(str(epub_path), 'zip', str(x))
            epub_zip_path = pathlib.Path(str(epub_path) + ".zip")
            epub_zip_path.rename(epub_path)
            epub.read_epub(epub_path)
            epub_path.unlink()
        except:
            print(f"An error has occurred with ID {x.name}")
            success = False
            break
    if success:
        print("all files are readable")
# Test to check whether there are equally many alto.xml files on datalab as the number as of pages obtained using the get_num_pages()-function

def unittest_altoxml():
    #ids = BLM.get_all_ids_BLM(566)
    pathcsv = pathlib.Path("corpus/metadata/edition.csv")
    df = pd.read_csv(pathcsv, index_col=False)
    success = True
    for id in ids:
        with open('/Documents/pw.txt', 'r') as file:
            pw = file.read().replace('\n', '')
        page = requests.get(f"https://datalab.kb.se/{id}/_view", auth=HTTPBasicAuth("demo", pw), stream=True)
        count = page.content.count(b'alto.xml')
        if count != -1:
            #num_pages = BLM.get_num_pages([id])[0]*3
            if count == num_pages:
                pass
            else:
                print(f'There are {count} number of alto.xml files which does not match the {num_pages} number of pages using the get_num_pages()-function')
                success = False
                break
        else:
            print(f'An alto_xml file does not exist for edition with edition_id {id} or does not match the number of pages using the get_num_pages()-function')
            success = False
            break
    if success:
        print('All files have the same number of alto.xml files (at least one) as the number of pages using the get_num_pages()-function')
# Test to check that there are no duplicate uuid's
def unittest_uuid():
    uuid_storage = []
    home_dir = str(Path.home())
    #ids = BLM.get_all_ids_BLM(566)

    for id in ids:
        edition = Path(f'{home_dir}/Documents/blm/corpus/editions/{id}/EPUB/content.xhtml')
        with open(edition, 'r') as f:
            xhtml_string = f.read()
            soup = BeautifulSoup(xhtml_string, 'html.parser')
            uuids = soup.find_all('pb')
            for pb_tag in uuids:
                uuid_value = pb_tag.get('uuid')
                uuid_storage.append(uuid_value)
    if len(set(uuid_storage)) == len(uuid_storage):
        print(f'There are {len(set(uuid_storage))} unique uuids without duplicates!')
    else:
        print(f'There are {len(set(uuid_storage))} unique uuids but {len(uuid_storage)} uuids in total!')

def test_all_articles():
    pathlist_contents = Path('corpus/editions').rglob('content.xhtml')
    all_articles_uuid = []

    xmlns='http://www.w3.org/1999/xhtml'

    for path in pathlist_contents:
        tree = ET.ElementTree(etree.parse(path))
        root = tree.getroot()


        for article in root.iterfind('.//{%s}article' % xmlns):

            article_uuid = article.attrib.get('uuid')
            
            all_articles_uuid.append(article_uuid)


    if len(all_articles_uuid) == len(set(all_articles_uuid)):
        print('all article uuids are unique')
        print(f'there are{len(all_articles_uuid)} elements')
    else:
        print(f'article uuid not unique, there are {len(all_articles_uuid)} article elements and only {len(set(all_articles_uuid))} unique uuids')

def test_all_pbs():
    pathlist_contents = Path('corpus/editions').rglob('content.xhtml')

    all_pbs_uuids = []

    xmlns='http://www.w3.org/1999/xhtml'

    for path in pathlist_contents:

        tree = ET.ElementTree(etree.parse(path))
        root = tree.getroot()

        for pb in root.iterfind('.//{%s}pb' % xmlns):

            pb_uuid = pb.attrib.get('uuid')
            
            all_pbs_uuids.append(pb_uuid)

    if len(all_pbs_uuids) == 0:
        print(f'Fail: there are 0 pb elements')

    elif len(all_pbs_uuids) == len(set(all_pbs_uuids)):
        print('all pb uuids are unique')
        print(f'there are {len(all_pbs_uuids)} pb elements')
    else:
        print(f'pb uuid not unique, there are {len(all_pbs_uuids)} pb elements and only {len(set(all_pbs_uuids))} unique uuids')

def test_all_headers():
    pathlist_contents = Path('corpus/editions').rglob('content.xhtml')

    all_headers_uuids = []

    xmlns='http://www.w3.org/1999/xhtml'

    for path in pathlist_contents:

        tree = ET.ElementTree(etree.parse(path))
        root = tree.getroot()

        for header in root.iterfind('.//{%s}header' % xmlns):

            header_uuid = header.attrib.get('uuid')
            
            all_headers_uuids.append(header_uuid)

    if len(all_headers_uuids) == 0:
        print(f'Fail: there are 0 header elements')

    elif len(all_headers_uuids) == len(set(all_headers_uuids)):
        print('all header uuids are unique')
        print(f'there are {len(all_headers_uuids)} header elements')
    else:
        print(f'header uuid not unique, there are {len(all_headers_uuids)} header elements and only {len(set(all_headers_uuids))} unique uuids')
    
def test_all_page_headers():
    pathlist_contents = Path('corpus/editions').rglob('content.xhtml')

    all_page_headers_uuids = []

    xmlns='http://www.w3.org/1999/xhtml'

    for path in pathlist_contents:

        tree = ET.ElementTree(etree.parse(path))
        root = tree.getroot()

        for page_header in root.iterfind('.//{%s}page_header' % xmlns):

            page_header_uuid = page_header.attrib.get('uuid')
            
            all_page_headers_uuids.append(page_header_uuid)

    if len(all_page_headers_uuids) == 0:
        print(f'Fail: there are 0 page_header elements')

    elif len(all_page_headers_uuids) == len(set(all_page_headers_uuids)):
        print('all page_header uuids are unique')
        print(f'there are {len(all_page_headers_uuids)} page_header elements')
    else:
        print(f'page_header uuid not unique, there are {len(all_page_headers_uuids)} page_header elements and only {len(set(all_page_headers_uuids))} unique uuids')

def main():

    unittest_epub()
    unittest_altoxml()
    unittest_uuid()
    test_all_articles()
    test_all_pbs()
    test_all_headers()
    test_all_page_headers()

if __name__ == "__main__":
    main()