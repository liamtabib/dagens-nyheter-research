import numpy as np,json
from pathlib import Path
from lxml import etree
import zipfile
from ebooklib import epub
import uuid
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


def compute_header_treshold(raw_file,quantile=0.80):
    """ read a content_json, and takes the q'th quantile the distribution of the font size of the words.
    Args:
        raw_file : content_json file of dagens nyheter.
        quantile : the q'th quantile in the interval [0,1]. 
    """
    size=[]
    for block in raw_file:
        #if empty content do nothing
        if block['content']=='':
            pass
        #otherwise take the sizes of the content
        else:
            font_information=block['font']
            for font in font_information:
                size.append(font['size'])
    #from string to float
    size=list(map(float,size))
    try:
        #numpy quantile
        return np.quantile(size,quantile)
    except Exception as e:
        raise Exception(f"An error occurred while computing the header threshold: {str(e)}")


def is_article(block,header_treshold):
    """ reads in a text block inside content_json file, and determines whether it indicates that an article is starting,
    based on a few heuristics, including the treshold computed from the entire edition. i.e. check if the block contains content that
    is larger than treshold. All subsequent text blocks that are not articles will be considered as text under the last found
     article.
    """
    font_information=block['font']
    num_words_in_block=len(block['content'].split())

    block_font_sizes=[]
    block_font_styles=[]
    block_font_families=[]
    for font in font_information:
        block_font_sizes.append(font['size'])
        block_font_styles.append(font['style'])
        block_font_families.append(font['family'])
        
    #get top font size
    max_size=max(list(map(float,block_font_sizes)))
    #choose a set of criterion to determine whether it is the start of an article
    #if 'Arial' in block_font_families and max_size>header_treshold and num_words_in_block>30:
    if max_size>header_treshold and num_words_in_block>47:
        return True
    else: return False


def page_link_structure(identifier):
    """ reads in a dagens nyheter edition id and returns the general shape of the image url in betalab.
    """
    json_dir_path = Path('files/raw_json/')
    #grab the structure file of the edition id
    structure_file = json_dir_path.rglob(f'{identifier}_structure.json')

    for file in structure_file:
        with file.open('r', encoding='utf-8') as f:
            raw_json = json.load(f)
    link_structure=raw_json[0]['has_part'][0]['has_representation'][1].split('.jp2')[0][:-4]

    return link_structure


def json_to_xml(json_content_path):
    """ reads a json content path, and builds an xml object,
        by parsing each text block into appropriate elements on the basis of article identification.
    """
    with json_content_path.open('r', encoding='utf-8') as f:
        raw_file = json.load(f)
        
    #get the general shape of the page link
    identifier=json_content_path.stem.split('_')[0]
    page_link_shape=page_link_structure(identifier)
    
    root=etree.Element('text')
    div_element=etree.SubElement(root,'div')
    div_element.set('type','preface')
    
    page_number='-1'
    header_treshold=compute_header_treshold(raw_file)
    for block in raw_file:
    
        block_content=block['content']

        if block_content=="":
            #check if block is empty
            pass
        
        else:
            
            if is_article(block,header_treshold):
                div_element=etree.SubElement(root,'div')
                div_element.set('type','article')
            else: pass

            current_page=block['@id'].split('#')[1][2]

            if current_page==page_number:
                #no new page
                pass
            else:
                pb_element=etree.SubElement(div_element, "pb")
                page_number=current_page
                num_zeros='0'*(4-len(page_number))
                page_link=page_link_shape+num_zeros+page_number+'.jp2/_view'
                pb_element.set("n",page_number)
                pb_element.set("facs",page_link)
                pb_element.set('xml_id',get_formatted_uuid())
    
            note_element=etree.SubElement(div_element, "note")
            note_element.set('xml_id',get_formatted_uuid())
            note_element.text = block_content
                    
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

    
def count_files():
    years=list(Path('corpus/epubs_json/').glob('*'))
    for year in years:
        n_epubs=len(list(Path(year).glob('*')))
        print(f'{year.name} has {n_epubs} epubs')


def process_content_file(file):
        #build an xml file
        epub_content = json_to_xml(file)
        #grab the name
        epub_name=file.stem.split('_')[0]
        year=file.parent.parent.name
        year_path =f'corpus/epubs_json/{year}'
        if os.path.exists(year_path):
            pass
        else:
            os.makedirs(year_path)
        #download the epub
        save_epub(epub_content,epub_name,Path(year_path))


def main():
    epub_dir_path = Path("corpus/epubs_json/")
    epub_dir_path.mkdir(parents=True, exist_ok=True)

    json_dir_path = Path('files/raw_json/')

    content_files = list(json_dir_path.rglob('*_content.json'))
    with multiprocessing.Pool() as pool:
        pool.map(process_content_file, content_files)
    #count epubs
    count_files()

if __name__ == '__main__':
    main()
