import pandas as pd
from unidecode import unidecode
import re
import random
import argparse
from tqdm import tqdm
import re
from pathlib import Path


def multiple_replace(text, i_start=192, i_end=383):
    d = [chr(c) for c in range(i_start, i_end + 1)]
    d = {c: unidecode(c) for c in d if c not in "åäö"}
    regex = re.compile("(%s)" % "|".join(map(re.escape, d.keys())))
    return regex.sub(lambda mo: d[mo.string[mo.start() : mo.end()]], text)


def process_text(text):
    text = text.lower()
    text = text.replace("-", "_")
    text = re.sub(r"[^a-zåäö\s\_]", "", text)
    text = multiple_replace(text)

    text = text.split()
    text = [c.strip("_") for c in text if len(c) > 1 and len(c) < 50]
    random.shuffle(text)
    text = " ".join(text)
    return text


def main():
  
    with open('topic_modelling/pclda_input/input.txt') as f:
        n = sum(1 for line in f)

    # Reader and writer
    with open('topic_modelling/pclda_input/input_clean.txt', "w") as writer, pd.read_csv(
        'topic_modelling/pclda_input/input.txt', sep="\t", header=None, chunksize=1000, dtype=str
    ) as reader:
        # Clean and write data in chunks
        for chunk in reader:
            chunk.iloc[:, 2] = chunk.iloc[:, 2].apply(process_text)
            txt = ["\t".join(row) for row in chunk.values.tolist()]
            writer.write("\n".join(txt))


if __name__ == "__main__":
    main()