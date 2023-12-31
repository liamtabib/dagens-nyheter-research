import xml.etree.ElementTree as ET
from pathlib import Path
from lxml import etree
import json
import nltk
import time
import multiprocessing
import regex
def align_block(xml_block , json_edition ,current_page):
    #json_edition is a parsed json file into dict
    
    xmlns='http://www.loc.gov/standards/alto/ns-v2#'

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

def test_regex_alignment(textline , block):

    corrected_textline = regex.search(textline, block, flags=regex.BESTMATCH)
    return corrected_textline.group()

def align_textline(textline , block):

    if len(textline) >= len(block):
        all_possible_textlines = [block]
    else:
        all_possible_textlines = [block[i : i+len(textline)] for i in range(0, len(block)-len(textline)+1)]

    corrected_textline = ''

    minimum_d = 1000
    for candidate_textline in all_possible_textlines:
        edit_d = nltk.edit_distance(textline,candidate_textline)

        if edit_d < minimum_d:
            minimum_d = edit_d
            corrected_textline = candidate_textline

    
    print('--------------------------------------------------------------------')
    print(textline)
    print(corrected_textline)
    print(minimum_d)
    print('--------------------------------------------------------------------')

    return corrected_textline

    
def segment(path_edition):

    xml_paths = list(Path(path_edition).glob('*'))
    xml_paths.sort()

    identifier=path_edition.stem
    current_page = '1'
    
    #find the correct json edition based on identifier
    json_dir_path = Path('files/raw_json/')
    path_json_editions = json_dir_path.rglob(f'{identifier}_content.json')

    for x in path_json_editions:
        with x.open('r', encoding='utf-8') as f:
            correct_json_ed = json.load(f)


    xmlns='http://www.loc.gov/standards/alto/ns-v2#'
    root=etree.Element('text')
    div_element=etree.SubElement(root,'div')
    div_element.set('type','preface')

    for xml_path in xml_paths:
        
        tree = ET.ElementTree(etree.parse(xml_path))
        for block in tree.iterfind('.//{%s}TextBlock' % xmlns):
            correct_json_block = align_block(block,correct_json_ed,current_page)


            for lines in block.iterfind('.//{%s}TextLine' % xmlns):
                textline_content=[]

                # Loop over all words in <TextLine>, find all child elements <String> 
                for word in lines.findall('{%s}String' % xmlns):
                    #get the size of the word

                    if 'SUBS_TYPE' in word.attrib:

                        if 'HypPart1' in word.attrib.get('SUBS_TYPE'):
                            fetch_word = word.attrib.get('SUBS_CONTENT')
                        else:
                            fetch_word = ''
                    else:
                        fetch_word = word.attrib.get('CONTENT')
                    textline_content.append(fetch_word)
                textline_content = ' '.join(textline_content)
                corrected_textline = align_textline(textline_content,correct_json_block)
                
        current_page = str (int(current_page) + 1)
        
def process_content_file(path_edition):
    segment(path_edition)

def main():

    xml_dir_path = Path('files/raw_xml/')

    path_editions = list(xml_dir_path.glob('*/*'))
    for x in path_editions:
        process_content_file(x)


if __name__ == '__main__':
    main()

