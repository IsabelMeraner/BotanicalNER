# usr/bin/env python3
# Isabel Meraner
# Project: Plant Name Recognition
# Institute of Computational Linguistics, University of Zurich

"""
Pipeline for semi-automated corpus annotation in IOB-tagging format.

Distinct dictionaries for German and Latin:
Latin|Scientific names:	lat_fam, lat_species (lat_phylum, lat_class, lat_subfam, lat_order, lat_genus)
German vernacular names: de_fam, de_species
"""

import argparse
from argparse import RawTextHelpFormatter
import os
from collections import defaultdict


def store_gazetteer(gazetteer):
    """
    Store all items of gazetteer in set structure.
    :param gazetteer (file-like object): one token per line
    :return: set containing all unique items of gazetteer file
    """

    return {line.rstrip("\n") for line in gazetteer}


def iter_gazetteers(gaz_storage, gaz_dir):
    gaz_names = []
    for file in sorted(os.listdir(gaz_dir)):
        if file.endswith(".txt"):
            # print("processing gazetteer {}".format(file))
            with open(gaz_dir + file, 'r') as gaz_file:
                gaz_name = file[:-4]
                gaz_names.append(gaz_name)
                gaz_storage[gaz_name] = store_gazetteer(gaz_file)

    return gaz_names


def count_longest_name(len_storage, gaz_storage, gaz_name_list):
    for gaz in gaz_name_list:
        max_len = 1
        # print("processing gazetteer storage: ", gaz)
        for name in gaz_storage[gaz]:
            # print(name)
            spaces = name.count(" ")  # count whitespaces
            if spaces > max_len:
                # print(name)
                max_len = spaces
        # print("Maximum length in gazetteer {} == {}".format(gaz, max_len))
        len_storage[gaz] = max_len


def get_unigram_indices(gaz_storage, sentence, gaz_name):
    all_indexes = []
    for plant_name in gaz_storage[gaz_name]:
        indexes = [index for index, token in enumerate(sentence) if token == plant_name]  # => [1, 3]
        # indexes = add_endings(plant_name, sentence)
        if indexes:
            # print("Found name '{}'  with position {}".format(plant_name, indexes))
            all_indexes.extend(indexes)

    return gaz_name, all_indexes


def get_multiword_indices(gaz_storage, sentence, gaz_name):
    all_indexes = []
    for plant_name in gaz_storage[gaz_name]:
        plant_name_list = plant_name.split(" ")
        token_length = len(plant_name_list)

        # if unigram in species list:
        if token_length == 1:
            indexes = [index for index, token in enumerate(sentence) if token == plant_name]  # => [1, 3]
            if indexes:
                # print("Treating unigram name '{}' of multiword gazetteer with position {}".format(plant_name, indexes))
                all_indexes.append(indexes)

        else:
            indexes = []
            for i, token in enumerate(range(len(sentence))):
                try:
                    subsequence = sentence[i:token_length]
                    # print(subsequence)

                    if subsequence == plant_name_list:
                        indexes.append((i, token_length))
                        # print("Found multiword name '{}'  with position {}".format(plant_name, indexes))
                    token_length += 1

                # reached end of sentence
                except IndexError:
                    continue
            if indexes:
                all_indexes.extend(indexes)

    return gaz_name, all_indexes


def get_sentence_indices(total_unigram_indices_per_sentence, total_multiword_indices_per_sentence):
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

    # print("ALL NUMERICAL INDICES: ", all_found_indices)
    return all_found_indices


def main():
    PATH = './../data_german/'

    # example gazetteers
    PATH_GAZ_V = './../gazetteers/de/'
    PATH_GAZ_L = './../gazetteers/lat/'

    parser = argparse.ArgumentParser(description='Annotate input files in IOB-scheme\n \
                                    run script like this: $ python3 iobannotate_corpus.py -d ./../dir_corpora -g de_gazetteers -l lat_gazetteer', formatter_class=RawTextHelpFormatter)

    parser.add_argument(
        '-d', '--directory',
        type=str,
        default=PATH,
        help='pass directory with data files for tagging')

    parser.add_argument(
        '-v', '--vernaculargazetteer',
        type=str,
        default=PATH_GAZ_V,
        help='pass directory with vernacular names gazetteer for tagging')

    parser.add_argument(
        '-l', '--latingazetteer',
        type=str,
        default=PATH_GAZ_L,
        help='pass directory with Latin names gazetteer for tagging')

    args = parser.parse_args()
    dir = args.directory
    gaz_dir_v = args.vernaculargazetteer
    gaz_dir_l = args.latingazetteer

    gaz_storage = defaultdict(set)
    len_storage = defaultdict(int)

    gaz_names_v = iter_gazetteers(gaz_storage, gaz_dir_v)
    gaz_names_l = iter_gazetteers(gaz_storage, gaz_dir_l)

    all_gazetteers = gaz_names_v + gaz_names_l

    # print("GAZETTEER NAMES: ", gaz_names_v, gaz_names_l)
    count_longest_name(len_storage, gaz_storage, gaz_names_v)
    count_longest_name(len_storage, gaz_storage, gaz_names_l)

    # print("Maximum counts in gazetteers: ", len_storage)
    unigram_gazetteers = []
    for name in all_gazetteers:
        if len_storage[name] == 1:
            unigram_gazetteers.append(name)
    # print("UNIGRAM GAZETTEERS: ", unigram_gazetteers)

    ngram_gazetteers = []
    for name in all_gazetteers:
        if len_storage[name] > 1:
            ngram_gazetteers.append(name)
    # print("NGRAM GAZETTEERS: ", ngram_gazetteers)

    # takes all files from training material folder
    for file in sorted(os.listdir(dir)):
        if file.endswith(".tok.pos.txt"):
            print("processing file {}".format(file))
            with open(dir + file, 'r') as infile, open(dir + "{}.iob.txt".format(file[:-4]), 'w',
                                                       encoding='utf-8') as outfile:
                sentence = []
                lemmas = []
                tags = []
                for line in infile:

                    # newline (end of sentence found)
                    if line == "\n":
                        #print(sentence)
                        sentence_string = " ".join(sentence)

                        total_unigram_indices_per_sentence = []
                        total_multiword_indices_per_sentence = []

                        for gazetteer in sorted(gaz_storage, key=lambda k: len(gaz_storage[k])):
                            # print(gazetteer)
                            if any(plantname in sentence_string for plantname in gaz_storage[gazetteer]):
                                # print("Found some plantname in gazetteer : {}".format(gazetteer))
                                if len_storage[gazetteer] == 1:
                                    # print("Tagging unigrams ....")
                                    gaz_name, unigram_indices = get_unigram_indices(gaz_storage, sentence, gazetteer)
                                    # print("Total unigram indices found: {}".format(unigram_indices))
                                    if unigram_indices:
                                        total_unigram_indices_per_sentence.append((gaz_name, unigram_indices))
                                else:
                                    # print("Tagging multiword names ....")
                                    gaz_name, multiword_indices = get_multiword_indices(gaz_storage, sentence,
                                                                                        gazetteer)
                                    # print("Total multi word indices found: {}".format(multiword_indices))
                                    if multiword_indices:
                                        total_multiword_indices_per_sentence.append((gaz_name, multiword_indices))

                        # print("---> TOTAL INDICES FOUND PER SENTENCE: \n\tUNIGRAMS: {}\n\tMULTIWORD: {}".format(
                        # total_unigram_indices_per_sentence, total_multiword_indices_per_sentence))

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
                                if FOUND == False:
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


if __name__ == "__main__":
    main()
