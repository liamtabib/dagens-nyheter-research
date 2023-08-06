from pathlib import Path
import json
import numpy as np


def font_information():
    content_files = Path('corpus/json_Dagens_nyheter/').rglob('*content.json')
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
    font_information()

if __name__ == '__main__':
    main()
