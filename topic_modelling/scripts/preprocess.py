import pandas as pd
from unidecode import unidecode
import re
import random
import argparse
from tqdm import tqdm
import re

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


def main(args):
    with open(args.input_path) as f:
        n = sum(1 for line in f)

    output_path=args.input_path.replace(".txt", "_clean.txt")

    # Reader and writer
    with open(output_path, "w") as writer, pd.read_csv(
        args.input_path, sep="\t", header=None, chunksize=args.chunksize, dtype=str
    ) as reader:
        # Clean and write data in chunks
        for chunk in tqdm(reader, total=n // args.chunksize):
            chunk.iloc[:, 2] = chunk.iloc[:, 2].apply(process_text)
            txt = ["\t".join(row) for row in chunk.values.tolist()]
            writer.write("\n".join(txt))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process corpus and Westac Hub files directories.')
    parser.add_argument('--input_path', type=str, help='Path to input.txt', default='topic_modelling/input.txt')
    parser.add_argument("--chunksize", "-c", type=int, default=1000)

    args = parser.parse_args()
    main(args)