import pandas as pd
from pathlib import Path
import os
import shutil
import json
import sys
import time


def write_separately_csv(rows):
    column_names = ["article_name", "article_index", "year"]
    total_obs = len(rows)
    done = False
    for n_parts in range(25,355):

        if total_obs % n_parts == 0:
            print(f'there are {n_parts} batches')
            csv_files_path =f'csv_batches'


            if os.path.exists(csv_files_path):
                pass

            else:
                os.makedirs(csv_files_path)


            for part in range(n_parts):
                lb = int((part/n_parts)*total_obs)
                ub = int(((part+1)/n_parts)*total_obs)

                df = pd.DataFrame(rows[lb:ub], columns=column_names)
                csv_name = '_' + str(part) + '.csv'
                csv_path = csv_files_path + '/' + csv_name

                df.to_csv(csv_path,index=False)
            done =True
            break
    if done:
        return
    else:
        print('number of rows is not divisible by number of parts, check csv_batches directory if it is empty')
        return -1


def main():
    """ reads in the dagens nyheter content and iterates over all blocks, storing the content as a row inside input.txt.
        Moreover, it also assigns indices to each block/document along with the year to documents.csv """
    base_directory = Path('../../westac_dn/raw_json/')

# Create an empty list to store the paths
    pathlist = []
    for year in range(1945, 1946):
        # Construct the directory path for the current year
        year_directory = base_directory / str(year)
        
        # Use rglob to find JSON files in the current year's directory
        json_files = year_directory.rglob('*content.json')
        
        # Extend the pathlist with the paths found for the current year
        pathlist.extend(json_files)
    
    txt_rows=[]
    csv_rows=[]
    article_index=0

    for json_content_path in pathlist:
        print(json_content_path)
        year = json_content_path.parent.parent.stem
        #get the identifier of utgåva
        edition_id=json_content_path.parent.stem

        with json_content_path.open('r', encoding='utf-8') as f:
            raw_file = json.load(f)

        path_meta = Path(f'../../westac_dn/raw_json/{year}/{edition_id}').rglob('*meta.json')

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
    print('starting to write input')
    with open('input.txt', 'w') as f:
        for row in txt_rows:
            f.write('\t'.join(row))
            f.write('\n')
    print('writing input finished')

    result = write_separately_csv(csv_rows)  # Get the return value of the function
    
    if result == -1:
        print('write_separately_csv returned -1. Stopping the script.')
        sys.exit()  # Exit the script
    


    print('Written csvs finished')

if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time_seconds = end_time - start_time
    execution_time_hours = execution_time_seconds / 3600  # 3600 seconds in an hour
    script_name = "generate_inputs_batches_dn.py"
    print(f"Script '{script_name}' executed in {execution_time_hours:.2f} hours.")