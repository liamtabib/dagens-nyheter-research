import numpy as np,json
from pathlib import Path
from lxml import etree
import zipfile
from ebooklib import epub
import uuid
import base58
import hashlib

def get_formatted_uuid(seed=None):
    if seed is None:
        x = uuid.uuid4()
    else:
        m = hashlib.md5()
        m.update(seed.encode('utf-8'))
        x = uuid.UUID(m.hexdigest())

    return f"i-{str(base58.b58encode(x.bytes), 'UTF8')}"


def compute_header_treshold(raw_file,quantile=0.80):
    size=[]
    for block in raw_file:
        if block['content']=='':
            pass
        else:
            font_information=block['font']
            for font in font_information:
                size.append(font['size'])
    
    size=list(map(float,size))
    try:
        return np.quantile(size,quantile)
    except Exception as e:
        raise Exception(f"An error occurred while computing the header threshold: {str(e)}")


def is_article(block,header_treshold): 
    font_information=block['font']
    num_words_in_block=len(block['content'].split(' '))

    block_font_sizes=[]
    block_font_styles=[]
    block_font_families=[]
    for font in font_information:
        block_font_sizes.append(font['size'])
        block_font_styles.append(font['style'])
        block_font_families.append(font['family'])
        
    #get top font size
    max_size=max(list(map(float,block_font_sizes)))
    #if 'Arial' in block_font_families and max_size>header_treshold and num_words_in_block>30:
    if max_size>header_treshold and num_words_in_block>47:
        return True
    else: return False


def page_link_structure(identifier):
    json_dir_path = Path('corpus/json_Dagens_nyheter/')

    structure_file = json_dir_path.glob(f'{identifier}_structure.json')

    for file in structure_file:
        with file.open('r', encoding='utf-8') as f:
            raw_json = json.load(f)
    link_structure=raw_json[0]['has_part'][0]['has_representation'][1].split('.jp2')[0][:-4]

    return link_structure


def json_to_xml(raw_file):
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
            #get the general shape of the page link
            identifier=block['@id'].split('#')[0].split('/')[-1]
            page_link_shape=page_link_structure(identifier)
            
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
                pb_element.set('xml:id',get_formatted_uuid())
    
            note_element=etree.SubElement(div_element, "note")
            note_element.set('xml:id',get_formatted_uuid())
            note_element.text = block_content
                    
    return etree.tostring(root, pretty_print=True)


def save_epub(epub_content,epub_name,epub_dir):
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


def main():
    epub_dir_path = Path("corpus/epubs/")
    epub_dir_path.mkdir(parents=True, exist_ok=True)

    json_dir_path = Path('corpus/json_Dagens_nyheter/')

    content_files = json_dir_path.glob('*_content.json')

    for file in content_files:

        with file.open('r', encoding='utf-8') as f:
            raw_content_json = json.load(f)
            epub_content = json_to_xml(raw_content_json)
            epub_name=file.stem.split('_')[0]
            save_epub(epub_content,epub_name,epub_dir_path)


if __name__ == '__main__':
    main()
