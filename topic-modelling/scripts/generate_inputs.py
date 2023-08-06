import pandas as pd
from lxml import etree
import xml.etree.ElementTree as ET
from pathlib import Path
import os
import shutil

def to_zip(data: pd.DataFrame, filename: str, archive_name: str, **csv_opts) -> None:
    data.to_csv(filename, compression=dict(method='zip', archive_name=archive_name), **csv_opts)

def main():
    """ reads in the dagens nyheter epub and iterates over all articles, storing the content as a row inside input.txt.
        Moreover, it also assigns indices to each article/document along with the year to documents.csv """
    pathlist = Path('corpus/epubs/').rglob('content.xhtml')
    txt_rows=[]
    csv_rows=[]
    article_index=0

    for path in pathlist:
        year = path.parts[2]
        #get the identifier of utgåva
        edition_id=path.parent.parent.stem
        tree = ET.ElementTree(etree.parse(path))
        #iterate through each <div type='article'> element
        for div_article in tree.iterfind(".//{http://www.w3.org/1999/xhtml}div[@type='article']"):
            article_content = ""
            #iterate through each <note> element
            for note in div_article.iterfind(".//{http://www.w3.org/1999/xhtml}note"):
                article_content += note.text.strip() + " "
            #create a name for each document, based on the identifier of the document and article index
            article_name=edition_id+str(article_index)
            # prepare a row to input.txt, with the columns of the index of the article, placeholder column, and article content
            txt_row=[str(article_index),'0',article_content]
            # prepare a row to document.csv, with the columns of the name of article, index, and article content
            csv_row=[article_name,str(article_index),str(year)]
            txt_rows.append(txt_row)
            csv_rows.append(csv_row)
            article_index+=1

    with open('topic-modelling/input.txt', 'w') as f:
        for row in txt_rows:
            f.write('\t'.join(row))
            f.write('\n')
    df = pd.DataFrame(csv_rows, columns=["article_name", "article_index", "year"])

    westac_hub_dir_path='topic-modelling/westac_hub_files'

    if os.path.exists(westac_hub_dir_path):
        shutil.rmtree(westac_hub_dir_path)
    os.makedirs(westac_hub_dir_path)

    to_zip(data=df,filename=f'{westac_hub_dir_path}/documents.zip',archive_name='documents.csv',sep='\t',index=False)


if __name__ == '__main__':
    main()