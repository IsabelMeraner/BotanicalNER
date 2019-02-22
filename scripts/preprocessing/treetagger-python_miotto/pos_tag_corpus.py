# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Annotate corpus with part-of-speech tags.

Output-file format:
CoNNL-2003

How to run the code:
$ python3 ./treetagger-python_miotto/pos_tag_corpus.py -d ./../../../resources/corpora/

Please note that the treetagger needs to be intalled.

"""

import argparse
import os
import sys
from treetagger import TreeTagger


def main():
    tt = TreeTagger(path_to_treetagger='/Applications/TreeTagger/',
                    language='german')

    PATH = './../corpora/testdata_fungi_animalia/'

    parser = argparse.ArgumentParser(description='Pos-tag all text files from input input_dir \
                                    run script like this: $ python3 pos_tag_corpus.py -d ./../dir_corpora')

    parser.add_argument(
        '-d', '--directory',
        type=str,
        default=PATH,
        help='pass directory with data files for tokenization')

    args = parser.parse_args()
    input_dir = args.directory

    for file in sorted(os.listdir(input_dir)):
        if file.endswith(".tok.txt"):
            print("processing file {}".format(file), file=sys.stderr, flush=True)
            with open(input_dir + file, 'r') as infile, open(input_dir + "{}.pos.txt".format(file[:-4]), 'w',
                                                       encoding='utf-8') as outfile:

                sentence = []
                sentences_per_file = []
                for line in infile:
                    if line == "\n":
                        sentence_string = " ".join(sentence)
                        sentences_per_file.append(sentence_string)
                        sentences_per_file.append("EOS")
                        sentence.clear()
                    else:
                        line = line.rstrip("\n")
                        sentence.append(line)

                all_tagged_sents = tt.tag([sent for sent in sentences_per_file])
                for elem in all_tagged_sents:
                    try:
                        token, tag, lemma = elem
                        if token == "EOS":
                            outfile.write("\n")
                        else:
                            outfile.write("{}\t{}\t{}\n".format(token, lemma, tag))
                    except ValueError:
                        print("ERROR in line :", elem, file=sys.stderr, flush=True)
                        if elem[0] == "\n":
                            pass

                sentences_per_file.clear()


if __name__ == "__main__":
    main()
