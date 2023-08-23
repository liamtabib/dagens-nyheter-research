import pandas as pd
from pathlib import Path
import os
import shutil
import json
def to_zip(data: pd.DataFrame, filename: str, archive_name: str, **csv_opts) -> None:
    data.to_csv(filename, compression=dict(method='zip', archive_name=archive_name), **csv_opts)

def main():
    """ reads in the dagens nyheter content and iterates over all blocks, storing the content as a row inside input.txt.
        Moreover, it also assigns indices to each block/document along with the year to documents.csv """
    pathlist = Path('../../../../data/westac_dn/raw_json').rglob('*content.json')
    txt_rows=[]
    csv_rows=[]
    article_index=0

    for json_content_path in pathlist:
        year = json_content_path.parent.parent.stem
        #get the identifier of utgåva
        edition_id=json_content_path.parent.stem

        with json_content_path.open('r', encoding='utf-8') as f:
            raw_file = json.load(f)

        path_meta = Path(f'../../../../data/westac_dn/raw_json/{year}/{edition_id}').rglob('*meta.json')

        for p_m in path_meta:
            with p_m.open('r', encoding='utf-8') as f:
                raw_meta = json.load(f)
                date = raw_meta['created']

        for block in raw_file:
    
            block_content=block['content']

            if block_content=="" or block["@type"] == "Image":
                #check if block is empty
                pass
            
            else:
                current_page=block['@id'].split('#')[1][2]
                #create a name for each document, based on the identifier of the document and article index
                article_name='DN_' + date + '_' + current_page + '_' +str(article_index)
                # prepare a row to input.txt, with the columns of the index of the article, placeholder column, and article content
                txt_row=[str(article_index),'0',block_content]
                # prepare a row to document.csv, with the columns of the name of article, index, and article year
                csv_row=[article_name,str(article_index),str(year)]
                txt_rows.append(txt_row)
                csv_rows.append(csv_row)
                article_index+=1

    with open('input.txt', 'w') as f:
        for row in txt_rows:
            f.write('\t'.join(row))
            f.write('\n')
    df = pd.DataFrame(csv_rows, columns=["article_name", "article_index", "year"])

    westac_hub_dir_path='westac_hub_files'

    if os.path.exists(westac_hub_dir_path):
        shutil.rmtree(westac_hub_dir_path)
    os.makedirs(westac_hub_dir_path)

    to_zip(data=df,filename=f'{westac_hub_dir_path}/documents.zip',archive_name='documents.csv',sep='\t',index=False)


if __name__ == '__main__':
    main()