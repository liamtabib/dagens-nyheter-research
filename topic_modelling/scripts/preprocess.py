import pandas as pd
from lxml import etree
import xml.etree.ElementTree as ET
from pathlib import Path
import json

def read_year(identifier):
    pathlist = Path('corpus/').rglob(f'{identifier}_meta.json')
    for path in pathlist:
        with path.open('r', encoding='utf-8') as f:

                raw_metadata = json.load(f)

                return raw_metadata['year']
        

def main():
     #TODO add remaining columns in the csv file
    pathlist = Path('corpus/').rglob('content.xhtml')
    txt_rows=[]
    csv_rows=[]
    article_index=0

    for path in pathlist:
        edition_id=path.parent.parent.stem
        tree = ET.ElementTree(etree.parse(path))
        year = read_year(edition_id)

        for div_article in tree.iterfind(".//{http://www.w3.org/1999/xhtml}div[@type='article']"):
            article_content = ""
            for note in div_article.iterfind(".//{http://www.w3.org/1999/xhtml}note"):
                article_content += note.text.strip() + " "
            
            article_name=edition_id+str(article_index)
            txt_row=[str(article_index),'0',article_content]
            csv_row=[article_name,str(article_index),str(year)]
            txt_rows.append(txt_row)
            csv_rows.append(csv_row)
            article_index+=1

    with open('topic_modelling/pcplda_input/input.txt', 'w') as f:
        for row in txt_rows:
            f.write('\t'.join(row))
            f.write('\n')
    df = pd.DataFrame(csv_rows, columns=["article_name", "article_index", "year"])
    df.to_csv('topic_modelling/westac_hub_input/documents.csv',index=False)

if __name__ == '__main__':
    main()