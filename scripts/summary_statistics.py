from pathlib import Path
import json
import numpy as np

def count_files():
    n_files=len(list(Path('corpus/json_Dagens_nyheter/').glob('*.json')))
    n_structure_files=len(list(Path('corpus/json_Dagens_nyheter/').glob('*structure.json')))
    n_content_files=len(list(Path('corpus/json_Dagens_nyheter/').glob('*content.json')))
    n_meta_files=len(list(Path('corpus/json_Dagens_nyheter/').glob('*meta.json')))
    print(f'there are {n_files} raw json files in total, of which {n_content_files} are content type,\
    {n_structure_files} are structure type, and {n_meta_files} are metadata type')


def year_interval():
    years=[]
    pathlist = Path('corpus/json_Dagens_nyheter/').glob('*meta.json')

    for path in pathlist:
        with path.open('r', encoding='utf-8') as f:
                raw_metadata = json.load(f)
                years.append(raw_metadata['year'])

    print(f'minimum year is {min(years)}, maximum year is {max(years)}')


def font_information():
    content_files = Path('corpus/json_Dagens_nyheter/').glob('*content.json')
    for file in content_files:
        d = {}
        d_num={}

        with file.open('r', encoding='utf-8') as f:
            raw_json = json.load(f)
            for block in raw_json:

                try:
                    font_information=block['font']
                    for x in font_information:
                        style=x['style']
                        size=x['size']
                        if style not in d:
                            d[style] = [size]
                            d_num[style]=1
                        else: 
                            d[style].append(size)
                            d_num[style]=d_num[style]+1
                            
                except KeyError:
                    pass
        print('Font, number of occurences, and average size in edition')
        for key, value in d.items():
            mean_size_value = round(np.mean(list(map(float, value))),1)
            print(key, d_num[key],mean_size_value)
        print('________________________________________________________')

def main():
    count_files()
    year_interval()
    font_information()

if __name__ == '__main__':
    main()
