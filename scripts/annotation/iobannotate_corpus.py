# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Dictionary-based annotation of input data in CoNLL-2003 IOB annotation format.

Uses language-specific gazetteers for English/German and Latin plant names:
— Latin|Scientific names:
lat_fam
lat_species
lat_phylum
lat_class
lat_subfam
lat_order
lat_genus
— German vernacular names
de_fam
de_species

# How to run the code:
$ python3 iobannotate_corpus.py -d ./../../resources/corpora/training_corpora/de/
  -v ./../../resources/gazetteers/de/ -s ./../../resources/gazetteers/lat/ -l de

"""

import argparse
import os
import sys
from collections import defaultdict


def store_gazetteer(gazetteer):
    """
    Store all items of gazetteer in set structure.

    :param gazetteer (file-like object): one plant name per line
    :return: set containing all unique items of gazetteer file
    """

    return {line.rstrip("\n") for line in gazetteer}


def iter_gazetteers(gaz_storage, gaz_dir):
    gaz_names = []
    for file in sorted(os.listdir(gaz_dir)):
        if file.endswith(".txt"):
            print(">> processing gazetteer {}".format(file), file=sys.stderr, flush=True)
            with open(gaz_dir + file, 'r') as gaz_file:
                gaz_name = file[:-4]
                gaz_names.append(gaz_name)
                gaz_storage[gaz_name] = store_gazetteer(gaz_file)

    return gaz_names


def count_longest_name(len_storage, gaz_storage, gaz_name_list):
    """
    Store maximum n-gram length per gazetteer file in dictionary.
    :param len_storage: dictionary containing maximum ngram length per gazetteer
    :param gaz_storage: gazetteer dictionary
    :param gaz_name_list: list with gazetteer names (corresponding to entity labels)
    :return:
    """
    for gaz in gaz_name_list:
        max_len = 1
        for name in gaz_storage[gaz]:
            spaces = name.count(" ")  # count whitespaces
            if spaces > max_len:
                max_len = spaces
        # print("Maximum length in gazetteer {} == {}".format(gaz, max_len), file=sys.stderr, flush=True)
        len_storage[gaz] = max_len


def get_unigram_indices(gaz_storage, sentence, gaz_name):
    """
    Get sentence indices of unigram plant names.

    :param gaz_storage: gazetteer dictionary
    :param sentence: list
    :param gaz_name: name of current gazetteer name
    :return: gaz_name, all_indices (gazetteer name and all found indices of plant names per sentence)
    """
    all_indices = []
    for plant_name in gaz_storage[gaz_name]:
        indexes = [index for index, token in enumerate(sentence) if token == plant_name]  # => [1, 3]
        if indexes:
            # print("Found name '{}'  with position {}".format(plant_name, indexes), file=sys.stderr, flush=True)
            all_indices.extend(indexes)

    return gaz_name, all_indices


def get_multiword_indices(gaz_storage, sentence, gaz_name):
    """
    Get sentence indices of multiword plant names.

    :param gaz_storage: gazetteer dictionary
    :param sentence: list
    :param gaz_name: name of current gazetteer name
    :return: gaz_name, all_indices (gazetteer name and all found indices of plant names per sentence)
    """
    all_indices = []
    for plant_name in gaz_storage[gaz_name]:
        plant_name_list = plant_name.split(" ")
        token_length = len(plant_name_list)

        # unigram cases in species gazetteerrs:
        if token_length == 1:
            indices = [index for index, token in enumerate(sentence) if token == plant_name]
            if indices:
                # print("Treating unigram name '{}' of multiword gazetteer with position {}".format(plant_name, indexes), file=sys.stderr, flush=True)
                all_indices.append(indices)

        else:
            indices = []
            for i, token in enumerate(range(len(sentence))):
                try:
                    subsequence = sentence[i:token_length]
                    if subsequence == plant_name_list:
                        indices.append((i, token_length))
                        # print("Found multiword name '{}'  with position {}".format(plant_name, indexes), file=sys.stderr, flush=True)
                    token_length += 1

                # reached end of sentence
                except IndexError:
                    continue
            if indices:
                all_indices.extend(indices)

    return gaz_name, all_indices


def get_sentence_indices(total_unigram_indices_per_sentence, total_multiword_indices_per_sentence):
    """
    Get all indices (unigram and multiword indices) per sentence.

    :param total_unigram_indices_per_sentence: list containing unigram
    :param total_multiword_indices_per_sentence: list containing ngram indices
    :return: all_found_indices (list containing all indices per sentence)
    """
    all_found_indices = []

    for gaz, all_pos in total_unigram_indices_per_sentence:
        for pos in all_pos:
            all_found_indices.append(pos)

    for gaz, all_pos in total_multiword_indices_per_sentence:
        for pos in all_pos:
            if isinstance(pos, tuple):
                start_index, end_index = pos
                all_found_indices.extend(range(start_index, end_index + 1))
            else:
                all_found_indices.extend(pos)

    return all_found_indices


def annotate_corpora(gaz_storage, len_storage, file, dir):
    """
    Annotate input file in iob-scheme using gazetteer lookups.
    
    :param gaz_storage: gazetteer dictionary
    :param len_storage: dictionary containing maximum ngram length per gazetteer
    :param file: file-like object, input corpus
    """

    with open("{}{}".format(dir, file), 'r') as infile, open("{}{}.iob.txt".format(dir, file[:-4]), 'w',
                                                             encoding='utf-8') as outfile:
        sentence = []
        lemmas = []
        tags = []
        for line in infile:
            if line == "\n":
                sentence_string = " ".join(sentence)
                total_unigram_indices_per_sentence = []
                total_multiword_indices_per_sentence = []

                for gazetteer in sorted(gaz_storage, key=lambda k: len(gaz_storage[k])):
                    if any(plantname in sentence_string for plantname in gaz_storage[gazetteer]):
                        # use this for English
                        # if any(plantname.lower() in sentence_string for plantname in gaz_storage[gazetteer]):
                        if len_storage[gazetteer] == 1:
                            gaz_name, unigram_indices = get_unigram_indices(gaz_storage, sentence, gazetteer)
                            if unigram_indices:
                                total_unigram_indices_per_sentence.append((gaz_name, unigram_indices))
                        else:
                            gaz_name, multiword_indices = get_multiword_indices(gaz_storage, sentence,
                                                                                gazetteer)
                            if multiword_indices:
                                total_multiword_indices_per_sentence.append((gaz_name, multiword_indices))

                all_indices_of_sentence = get_sentence_indices(total_unigram_indices_per_sentence,
                                                               total_multiword_indices_per_sentence)

                block_startend_indices = []

                INSIDE_MEMORY = False
                for index, (token, lemma, tag) in enumerate(zip(sentence, lemmas, tags)):
                    FOUND = False
                    if index in all_indices_of_sentence:
                        for gaz_name_multi, positions in total_multiword_indices_per_sentence:
                            for pos in positions:
                                if isinstance(pos, tuple):
                                    start_index, end_index = pos
                                    block_startend_indices.extend(range(start_index, end_index + 1))
                                    if index == start_index:
                                        outfile.write("{}\t{}\t{}\t{}\n".format(token, lemma, tag,
                                                                                'B-{}'.format(gaz_name_multi)))
                                        FOUND = True
                                        INSIDE_MEMORY = True
                                    elif INSIDE_MEMORY and start_index < index < end_index:
                                        FOUND = True
                                        outfile.write("{}\t{}\t{}\t{}\n".format(token, lemma, tag,
                                                                                'I-{}'.format(gaz_name_multi)))
                                    elif INSIDE_MEMORY and index == (end_index - 1):
                                        outfile.write("{}\t{}\t{}\t{}\n".format(token, lemma, tag,
                                                                                'I-{}'.format(gaz_name_multi)))
                                        INSIDE_MEMORY = False
                                else:
                                    for single_pos in pos:
                                        if single_pos in block_startend_indices:
                                            continue
                                        else:
                                            if index == single_pos:
                                                block_startend_indices.append(single_pos)
                                                FOUND = True
                                                outfile.write("{}\t{}\t{}\t{}\n".format(token, lemma, tag,
                                                                                        'B-{}'.format(
                                                                                            gaz_name_multi)))

                        # treat unigram lists (de-fam, lat-fam, -genus, -subfam, -phylum, -class, -order)
                        for gaz_name_uni, positions_uni in total_unigram_indices_per_sentence:
                            for single_pos in positions_uni:
                                if single_pos in block_startend_indices:
                                    continue
                                else:
                                    if index == single_pos:
                                        FOUND = True
                                        block_startend_indices.append(single_pos)
                                        outfile.write("{}\t{}\t{}\t{}\n".format(token, lemma, tag,
                                                                                'B-{}'.format(gaz_name_uni)))

                    else:
                        if not FOUND:
                            outfile.write("{}\t{}\t{}\t{}\n".format(token, lemma, tag, 'O'))

                outfile.write("\n")
                block_startend_indices.clear()

                sentence.clear()
                lemmas.clear()
                tags.clear()
                total_unigram_indices_per_sentence.clear()
                total_multiword_indices_per_sentence.clear()

            else:
                token, lemma, tag = line.rstrip("\n").split("\t")
                sentence.append(token)
                lemmas.append(lemma)
                tags.append(tag)


def main():
    PATH = './../../resources/corpora/training/corpora/de/'
    PATH_GAZ_V = './../../resources/gazetteers/de/'
    PATH_GAZ_L = './../../resources/gazetteers/lat/'

    parser = argparse.ArgumentParser(
        description='Annotate tokenized input files using gazetteer lookups in IOB format.')

    parser.add_argument(
        '-d', '--directory',
        type=str,
        default=PATH,
        help='input directory with corpus files for annotation')

    parser.add_argument(
        '-v', '--vernaculargazetteer',
        type=str,
        default=PATH_GAZ_V,
        help='vernacular names gazetteers for annotation')

    parser.add_argument(
        '-s', '--scientificgazetteer',
        type=str,
        default=PATH_GAZ_L,
        help='Latin names gazetteers for annotation')

    parser.add_argument(
        '-l', '--language',
        type=str,
        default="de",
        help='Language code {de|en} for input data')

    args = parser.parse_args()
    dir = args.directory
    gaz_dir_v = args.vernaculargazetteer
    gaz_dir_l = args.latingazetteer
    language = args.language

    gaz_storage = defaultdict(set)
    len_storage = defaultdict(int)

    gaz_names_v = iter_gazetteers(gaz_storage, gaz_dir_v)
    gaz_names_l = iter_gazetteers(gaz_storage, gaz_dir_l)

    all_gazetteers = gaz_names_v + gaz_names_l

    print(">> {} GAZETTEER NAMES:\n{}\n{} ".format(language, gaz_names_v, gaz_names_l), file=sys.stderr, flush=True)
    count_longest_name(len_storage, gaz_storage, gaz_names_v)
    count_longest_name(len_storage, gaz_storage, gaz_names_l)

    print(">> Maximum counts in gazetteers: {}".format(len_storage), file=sys.stderr, flush=True)

    unigram_gazetteers = []
    for name in all_gazetteers:
        if len_storage[name] == 1:
            unigram_gazetteers.append(name)
    print(">> UNIGRAM GAZETTEERS:\n{} ".format(unigram_gazetteers), file=sys.stderr, flush=True)

    ngram_gazetteers = []
    for name in all_gazetteers:
        if len_storage[name] > 1:
            ngram_gazetteers.append(name)
    print(">> NGRAM GAZETTEERS:\n{} ".format(ngram_gazetteers), file=sys.stderr, flush=True)

    for file in sorted(os.listdir(dir)):
        if file.endswith(".tok.pos.txt"):
            print(">> processing file {}".format(file), file=sys.stderr, flush=True)
            annotate_corpora(gaz_storage, len_storage, file, dir)

    print(">> [DONE]: IOB-annotation is done for input dir {} ".format(dir), file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
