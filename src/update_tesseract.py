import xml.etree.ElementTree as ET
from pathlib import Path
from lxml import etree
import json
import nltk
import time
import multiprocessing

#for inspiration
def align_block(xml_block , json_edition ,current_page):
    
    xmlns= 'http://www.w3.org/1999/xhtml'

    block_content= []

    for lines in xml_block.iterfind('.//{%s}TextLine' % xmlns):

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
        
    xml_block_content = ' '.join(block_content)
    
    #iterate through each json block and find the shortest edit distance
    minimum_d = 1000
    correct_json_block = ''
    for json_block in json_edition:
        if f'#1-{current_page}' in json_block['@id'] and json_block['@type'] == 'Text':
            edit_d = nltk.edit_distance(xml_block_content,json_block['content'])

            if edit_d < minimum_d:
                minimum_d = edit_d
                correct_json_block = json_block['content']

    return correct_json_block


def align_block_(epub_page,json_page_blocks):
    correct_epub_page = {} # element uuid: element Tesseract text

    #merge values of epub_page dict into string, and match json page blocks
    #append each element uuid with the corrected content into correct_epub_page dict
    return correct_epub_page

def iterator(path_to_epub):

    edition_id=path_to_epub.parent.parent.stem
    json_dir_path = Path('../dn-extra/files/raw_json/')
    path_json_editions = json_dir_path.rglob(f'{edition_id}_content.json')

    for x in path_json_editions:
        with x.open('r', encoding='utf-8') as f:
            correct_json_ed = json.load(f)

    tree = ET.ElementTree(etree.parse(path_to_epub))
    xmlns= 'http://www.w3.org/1999/xhtml'


    for page in tree.iterfind('.//{%s}pb' % xmlns):
        page_number = page.attrib.get('n')

        epub_page = {} # element uuid: element text
        json_page_blocks = [] #list of json blocks of page

        #find the json blocks that are of this page and append to json_page_blocks
    
        #iterate over elements inside this page, populate epub_page dict with all elements between two consecutive pbs

        correct_epub_page = align_block_(epub_page,json_page_blocks)
    
        # iterate again on the elements, this time replacing the element content with the key value inside epub

        




def main():

    pathlist = Path('corpus/epubs_xml/').rglob('content.xhtml')

    for path in pathlist:
        iterator(path)

if __name__ == '__main__':
    main()

