import xml.etree.ElementTree as ET
from pathlib import Path
import zipfile
from ebooklib import epub
from lxml import etree
import numpy as np
import uuid
import json
import base58
import hashlib
import multiprocessing
import os


def get_formatted_uuid(seed=None):
    if seed is None:
        x = uuid.uuid4()
    else:
        m = hashlib.md5()
        m.update(seed.encode('utf-8'))
        x = uuid.UUID(m.hexdigest())

    return f"i-{str(base58.b58encode(x.bytes), 'UTF8')}"


def styles_mapping(xml_tree):
    xmlns='http://www.loc.gov/standards/alto/ns-v2#'

    styles_font={}
    styles=xml_tree.find(('.//{%s}Styles' % xmlns))
    for children in styles.findall('{%s}TextStyle' % xmlns):
        styles_font[children.attrib.get('ID')]=children.attrib.get("FONTSIZE")
    
    return styles_font


def compute_header_treshold(xml_paths,quantile=0.90):
    """ takes the q'th quantile the distribution of the font size of the words.
    Args:
        xml_paths : path to xml files for edition.
        quantile : the q'th quantile in the interval [0,1]. 
    """

    size=[]
    xmlns='http://www.loc.gov/standards/alto/ns-v2#'

    for xml_path in xml_paths:

        tree = ET.ElementTree(etree.parse(xml_path))

        styles_font = styles_mapping(tree)

        for lines in tree.iterfind('.//{%s}TextLine' % xmlns):

            for line in lines.findall('{%s}String' % xmlns):
                # Check if there are no hyphenated words
                if ('SUBS_CONTENT' not in line.attrib and 'SUBS_TYPE' not in line.attrib):
                # Get value of attribute @CONTENT from all <String> elements
                    style=line.attrib.get('STYLEREFS')
                    size.append(styles_font[style])

                else:
                    if ('HypPart1' in line.attrib.get('SUBS_TYPE')):
                        style=line.attrib.get('STYLEREFS')
                        size.append(styles_font[style])

    #from string to float
    size=list(map(float,size))
    try:
        #numpy quantile
        return np.quantile(size,quantile)
    except Exception as e:
        raise Exception(f"An error occurred when taking the quantile: {str(e)}")


def page_link_structure(identifier):
    """ reads in a dagens nyheter edition id and returns the general shape of the image url in betalab.
    """
    json_dir_path = Path('../dn-extra/files/raw_json/')
    #grab the structure file of the edition id
    structure_file = json_dir_path.rglob(f'{identifier}_structure.json')

    for file in structure_file:
        with file.open('r', encoding='utf-8') as f:
            raw_json = json.load(f)
    link_structure=raw_json[0]['has_part'][0]['has_representation'][1].split('.jp2')[0][:-4]

    return link_structure


def segment(path_edition):
    """ reads a directory path to a edition with xml files, and builds an xml object,
        by parsing each text block into appropriate elements on the basis of article identification.
    """

    xml_paths = list(Path(path_edition).glob('*'))
    xml_paths.sort()

    identifier=path_edition.stem
    page_link_shape=page_link_structure(identifier)
    xmlns='http://www.loc.gov/standards/alto/ns-v2#'
    header_treshold=compute_header_treshold(xml_paths)

    root=etree.Element('text')
    div_element=etree.SubElement(root,'div')
    div_element.set('type','preface')
    current_page = '1'

    for xml_path in xml_paths:

        pb_element=etree.SubElement(div_element, "pb")

        num_zeros='0'*(4-len(current_page))
        page_link=page_link_shape+num_zeros+current_page+'.jp2/_view'

        pb_element.set("n",current_page)
        pb_element.set("facs",page_link)
        pb_element.set('xml_id',get_formatted_uuid())

        tree = ET.ElementTree(etree.parse(xml_path))
        styles_font = styles_mapping(tree)

        for lines in tree.iterfind('.//{%s}TextLine' % xmlns):
            header_line = False
            page_header_line = False
            textline_content=[]

            if int(lines.attrib.get('VPOS')) < 160:
                page_header_line = True
            elif int(lines.attrib.get('VPOS')) < 250:
                for word in lines.findall('{%s}String' % xmlns):
                    if word.attrib.get('CONTENT').isupper():
                         page_header_line = True

            # Loop over all words in <TextLine>, find all child elements <String> 
            for word in lines.findall('{%s}String' % xmlns):
                #get the size of the word
                word_style=word.attrib.get('STYLEREFS')  
                word_size=float(styles_font[word_style])

                if 'SUBS_TYPE' in word.attrib:

                    if 'HypPart1' in word.attrib.get('SUBS_TYPE'):
                        fetch_word = word.attrib.get('SUBS_CONTENT')
                    else:
                        fetch_word = ''
                else:
                    fetch_word = word.attrib.get('CONTENT')
                textline_content.append(fetch_word)
                # Check if the word is a header based on the treshold computed, no words consisting of only digits or special characters can be headers
                if word_size > header_treshold and not all(c in "\!@#$%^&*()-+?_=,<>/0123456789" for c in fetch_word):
                    header_line = True
            
            textline_content = ' '.join(textline_content)


            if textline_content=="":
                #check if line is empty
                pass
            
            else:
                
                if page_header_line:
                    element=etree.SubElement(div_element, "page_header")

                elif header_line:

                    if 'element' in locals():
                        if element.tag == 'header':
                            pass
                        else:
                            div_element=etree.SubElement(root,'div')
                            div_element.set('type','article')
                    else:                  
                        div_element=etree.SubElement(root,'div')
                        div_element.set('type','article')
                        
                    element=etree.SubElement(div_element, "header")     

                else:
                    element=etree.SubElement(div_element, "content")     
    
                element.set('xml_id',get_formatted_uuid())
                element.text = textline_content                

        current_page = str (int(current_page) + 1)

    return etree.tostring(root, pretty_print=True)


def save_epub(epub_content,epub_name,epub_dir):
    """ creates epub out of an xml object.
    Args:
        epub_content : xml etree string
        epub_name : file name of the resulting epub
        epub_dir : save directory 
    """
    book = epub.EpubBook()
    book.set_identifier(epub_name)
    book.set_title("Sample book")
    book.set_language("sv")
    # create content in one chapter
    c1 = epub.EpubHtml(title=epub_name, file_name="content.xhtml", lang="sv")
    c1.content = epub_content
    book.add_item(c1)
    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    # define CSS style
    style = "BODY {color: white;}"
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style,
    )
    # add CSS file
    book.add_item(nav_css)
    # basic spine
    book.spine = ["nav", c1]

    # write to the file
    epub.write_epub(f"{epub_name}.epub", book)
    newpath = epub_dir / epub_name
    Path(newpath).mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(f"{epub_name}.epub", 'r') as zip_ref:
        zip_ref.extractall(newpath)
    Path(f"{epub_name}.epub").unlink()


def process_content_file(path_edition):
        #build an xml file
        epub_content = segment(path_edition)
        #grab the name
        epub_name=path_edition.stem.split('_')[0]
        year=path_edition.parent.name
        year_path =f'corpus/epubs_xml/{year}'
        if os.path.exists(year_path):
            pass
        else:
            os.makedirs(year_path)
        #download the epub
        save_epub(epub_content,epub_name,Path(year_path))


def count_files():
    years=list(Path('corpus/epubs_xml/').glob('*'))
    for year in years:
        n_epubs=len(list(Path(year).glob('*')))
        print(f'{year.name} has {n_epubs} epubs')


def main():
    epub_dir_path = Path("corpus/epubs_xml/")
    epub_dir_path.mkdir(parents=True, exist_ok=True)

    xml_dir_path = Path('../dn-extra/files/raw_xml/')

    path_editions = list(xml_dir_path.glob('*/dark-*'))
    
    with multiprocessing.Pool() as pool:
       pool.map(process_content_file, path_editions)
    #count epubs
    count_files()

if __name__ == '__main__':
    main()