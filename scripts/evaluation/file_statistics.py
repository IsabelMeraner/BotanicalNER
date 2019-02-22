# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Cómpute file statistics for each corpus resource:
Number of sentences, avg. length of sentences, no. of tokens / types, avg. token length, mumber of entity labels per resource.

How to run the code:
$ python3 file_statistics.py -i ./../../resources/corpora/training_corpora/de/

"""
import argparse
import os
import sys
from collections import defaultdict


def iter_file(infile):
    """
    Iterate over file and extract relevant statistical information about the corpus data and the present entity labels.
    :param infile: file-like object
    :return: sentence_counter, sentence_length, token_counter, token_length, unique_types, tag_counter, unique_tag_counter
    """
    sentence_counter = 0
    token_counter = 0
    tag_counter = defaultdict(int)
    unique_tag_counter = defaultdict(int)
    token_length, sentence_length, sentence = [], [], []
    unique_types = defaultdict(int)

    for line in infile:
        if line == "\n":
            sentence_counter += 1
            sentence_length.append(len(sentence))
            sentence.clear()
        else:
            token, lemma, pos, iob = line.rstrip("\n").split("\t")
            token_counter += 1
            sentence.append(token)
            token_length.append(len(token))
            unique_types[token] += 1
            if iob == "O":
                continue
            tag_counter[iob[2:]] += 1
            unique_tag_counter[(iob[2:], token)] += 1

    return sentence_counter, sentence_length, token_counter, token_length, unique_types, tag_counter, unique_tag_counter


def main():
    INPUT_DIR = './../../resources/corpora/de/'

    parser = argparse.ArgumentParser(
        description='Get file statistics')

    parser.add_argument(
        '-i', '--input_directory',
        type=str,
        default=INPUT_DIR,
        help='input directory containing files in CoNNL-2003 format with IOB annotations')

    args = parser.parse_args()
    input_directory = args.input_directory

    for file in os.listdir(input_directory):
        if file.endswith("iob.txt"):
            with open(input_directory + file, 'r') as infile:

                sentence_counter, sentence_length, token_counter, token_length, unique_types, tag_counter, unique_tag_counter = iter_file(
                    infile)

                print("\n\n", 40 * "#", file=sys.stderr, flush=True)
                print("total sentences for file {}\n = {}".format(file, sentence_counter), file=sys.stderr, flush=True)
                print("total tokens (incl. punctuation) for file {}\n = {}".format(file, token_counter),
                      file=sys.stderr, flush=True)
                print("Mean SENTENCE Length: {}".format(sum(sentence_length) / len(sentence_length)), file=sys.stderr,
                      flush=True)
                print("Mean TOKEN Length: {}".format(sum(token_length) / len(token_length)), file=sys.stderr,
                      flush=True)
                print("Unique TYPES: {}\n".format(len(unique_types)), file=sys.stderr, flush=True)

                print("total occurrences of tags: \n{}".format(sorted(tag_counter.items())), file=sys.stderr,
                      flush=True)
                print("no. of tags (total): {}".format(sum(tag_counter.values())), file=sys.stderr, flush=True)
                print("vs. unique occurrences of tags: {}".format(len(unique_tag_counter)), file=sys.stderr, flush=True)

                total = sum(tag_counter.values())
                unique = len(unique_tag_counter)
                perc = (unique / total) * 100
                print("Percentage total/unique of tags: {}%".format(perc), file=sys.stderr, flush=True)

                count_distinct = defaultdict(int)
                for (tag, token), count in sorted(unique_tag_counter.items()):
                    count_distinct[tag] += 1
                print("Distinct tags: {}".format(sorted(count_distinct.items())), file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
