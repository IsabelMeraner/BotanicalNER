# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Tokenize input text file and re-merge sentences at botanical abbreviations.

Output format:
1 token per line, sentence boundaries are marked by additional newline (CoNLL-2003 format).

How to run the code:
$ python3 tokenize_corpus.py -d ./../raw_data/ -l de
"""

import argparse
import os
import spacy
import sys
from nltk import word_tokenize
from nltk.tokenize import sent_tokenize

def fix_tokenization(tokens, bot_abbreviations):
    """
    Fix erroneous segmentation at botanical abbreviations.

    :param tokens: tokenized sentence
    :param bot_abbreviations: list of botanical abbreviations
    :return: fixed tokens: list of corrected tokenized sentence
    """

    fixed_tokens = []
    for i, token in enumerate(tokens):
        try:
            if str(tokens[i]) + str(tokens[i + 1]) in bot_abbreviations:
                fixed_tokens.append(str(tokens[i]) + ".")
                del tokens[i + 1]
            else:
                fixed_tokens.append(str(token))
        except IndexError:
            fixed_tokens.append(str(token))
            continue

    return fixed_tokens


def tokenize_input(inputText, language, nlp):
    """
    Tokenize input using a language-specific tokenizer (spaCy for English, NLTK for German)

    :param inputText: (str) input line containing one or more sentences
    :param language: (str) iso-language code ('de' or 'en')
    :return: fixed_tokens: (list) of tokens per sentence
    """

    bot_abbreviations = ["var.", "convar.", "agg.", "ssp.", "sp.", "subsp.", "x.", "L.",
                         "auct.", "comb.", "illeg.", "cv.", "emend.", "al.", "f.", "hort.",
                         "nm.", "nom.", "ambig.", "cons.", "dub.", "superfl.", "inval.", "nov.",
                         "nud.", "rej.", "nec.", "nothosubsp.", "p.", "hyb.", "syn.", "synon."]

    if language == 'de':
        sent_tokenize_list = sent_tokenize(inputText, 'german')
    elif language == 'en':
        sent_tokenize_list = sent_tokenize(inputText)
    else:
        raise NotImplementedError("Please make sure to chose one of the following languages (de, en).")

    # fix erroneous sentence segmentation
    fixed_sentences = []
    for i, sent in enumerate(sent_tokenize_list):
        if sent_tokenize_list[i].split()[-1] in bot_abbreviations:
            fixed_sentences.append(sent_tokenize_list[i] + " " + sent_tokenize_list[i + 1])
            del sent_tokenize_list[i + 1]
        else:
            fixed_sentences.append(sent)

    for sent in fixed_sentences:
        if language == 'de':
            tokens = word_tokenize(sent, 'german')
            fixed_tokens = fix_tokenization(tokens, bot_abbreviations)
        elif language == 'en':
            tokens = list(nlp(sent))
            fixed_tokens = fix_tokenization(tokens, bot_abbreviations)

    return fixed_tokens


def main():
    PATH = './../../../resources/corpora/training_corpora/'
    parser = argparse.ArgumentParser(description='Tokenize all text files from input input_dir \
                                    run script like this: $ python3 tokenize_corpus.py -d ./../dir_corpora')

    parser.add_argument(
        '-d', '--directory',
        type=str,
        default=PATH,
        help='pass directory with data files for tokenization')

    parser.add_argument(
        '-l', '--language',
        type=str,
        default='de',
        help='iso language code {de | en}')

    args = parser.parse_args()
    input_dir = args.directory
    language = args.language

    assert language in ["de", "en"]
    nlp = spacy.load("en")

    for file in sorted(os.listdir(input_dir)):
        if file.endswith(".txt") and ".tok." not in file:
            print(">> processing file {}".format(file), file=sys.stderr, flush=True)
            with open(input_dir + file, 'r') as infile, open(input_dir + "{}.tok.txt".format(file[:-4]), 'w',
                                                             encoding='utf-8') as outfile:
                for line in infile:
                    if not line or line.startswith("#"):
                        continue
                    line = line.rstrip("\n")
                    tokens = tokenize_input(line, language, nlp)
                    for token in tokens:
                        outfile.write(token + "\n")
                    outfile.write("\n")


if __name__ == "__main__":
    main()
