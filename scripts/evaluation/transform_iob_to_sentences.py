# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Transform tab-separated files (CoNLL-2003 format with IOB-annotations) into 1 sentence per line as expected by the tagger.py script of Lample (2016).

# How to run the code:
$ python3 transform_iob_to_sentences.py -i ./../../resources/corpora/training_corpora/de/botlit_corpus_de.tok.pos.iob.txt -o botlit_sentences.txt


"""

import argparse


def transform_to_sentences(infile, outfile):
    """
    Iterate over file and transform each sentence from CoNNL-2003 format into 1 (tokenized (sentence per line.
    :param infile: file-like object (in CoNNL-2003 format)
    :param outfile: file-like object (1 tokenized sentence per line format)
    """
    sentence = []
    for line in infile:
        if line == "\n":
            outfile.write(" ".join(sentence) + "\n")
            sentence.clear()
        else:
            line_split = line.rstrip("\n").split("\t")
            sentence.append(line_split[0])


def main():
    INPUT = "./../../resources/corpora/training_corpora/de/botlit_corpus_de.tok.pos.iob.txt"
    OUTPUT = "./../../resources/corpora/training_corpora/de/botlit_out"

    parser = argparse.ArgumentParser(
        description='Transform CoNNL-2003 format into 1 tokenized sentence per line.')

    parser.add_argument(
        '-i', '--input_file',
        type=str,
        default=INPUT,
        help='input file in CoNNL-2003 format with IOB annotations')

    parser.add_argument(
        '-o', '--output_file',
        type=str,
        default=OUTPUT,
        help='output file: 1 sentence per line (tokenized)')

    args = parser.parse_args()
    input_file = args.input_file
    output_file = args.output_file

    with open(input_file, 'r') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        transform_to_sentences(infile, outfile)


if __name__ == '__main__':
    main()
