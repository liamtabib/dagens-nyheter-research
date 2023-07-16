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
    d = {}
    content_files = Path('corpus/json_Dagens_nyheter/').glob('*content.json')
    for file in content_files:

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
                        else: d[style].append(size)
                            
                except KeyError:
                    pass

    for key, value in d.items():
        mean_size_value = np.mean(list(map(float, value)))
        print(key, mean_size_value)

def main():
    count_files()
    year_interval()
    font_information()

if __name__ == '__main__':
    main()
