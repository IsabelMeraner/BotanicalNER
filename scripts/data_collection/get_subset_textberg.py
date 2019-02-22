# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Extract sentences with botanical content for the creation of a subcorpus from Text+Berg data.
Use gazetteers to retrieve the sentences for the subset containing at least one Latin
or verncular plant name.
Apply cleaning of sentences to avoid listings, ocr-errors, short sentences.

How to run the code:
$ python3 get_subset_textberg.py -i ./../TextBerg/SAC/ -o ./subset_textberg_de.txt
  -g ./../../resources/gazetteers/ -l de
"""

import argparse
import sys
import os
import lxml.etree as ET


def _parse_xml(infile):
    """
    Iterate over sentences in XML file.
    :param infile: (file-like obj) XML-file from T+B corpus
    :return: generator over sentences
    """
    for _, book in ET.iterparse(infile, tag='book'):
        for sentence in book.iterfind('.//s'):
            sent = []
            if sentence.get('lang') == 'de':
                for word in sentence.iterfind('.//w'):
                    sent.append(word.text)
                yield " ".join(sent)
                sent.clear()


def construct_set(input_file):
    """
    Create set of unique gazetteer names
    :param input_file:
    :return: set of names
    """

    return {line.rstrip("\n") for line in input_file}


def _load_gazetteers(PATH_GAZ, language):
    """
    Load gazetteers from files and store them in set structure.
    :param PATH_GAZ: file path to directory containing gazetteer files
    :param language: str language iso code {de|en}
    :return: fam_set, species_set, lat_fam_set, lat_species_set (set)
    """
    file_fam = '{}/{}_fam.txt'.format(language, language)

    # chose subset of de species names
    file_species = '{}/{}_species.txt'.format(language, language)

    file_lat_fam = 'lat/lat_fam.txt'
    file_lat_genus = 'lat/lat_genus.txt'  # use genus instead of species

    with open(PATH_GAZ + file_fam, 'r') as fam_file, \
            open(PATH_GAZ + file_species, 'r') as species_file, \
            open(PATH_GAZ + file_lat_fam, 'r') as lat_fam_file, \
            open(PATH_GAZ + file_lat_genus, 'r') as lat_genus_file:
        fam_set, species_set, lat_fam_set, lat_genus_set = construct_set(fam_file), \
                                                             construct_set(species_file), construct_set(
            lat_fam_file), construct_set(lat_genus_file)

        # remove too general name, like "Familie", "Familien" from set
        fam_set -= {"Familie", "Familien", "", " "}
        species_set -= {"", " ", "Winde"}
        lat_fam_set -= {"", " "}
        #lat_species_set -= {"", " "}
        lat_genus_set -= {"", " ", "Asia", "India", "Phoenix", "Johnson", "Argentina", "Mexico", "Namibia", "Nima",
                          "Paris", "Manga", "page", "Martha", "Disastser", "King", "Piper", "Georgia", "Aron",
                          "Quechua", "Victoria", "Side", "Kali", "Puya", "Anna", "Ruth", "Dorothea", "Cornelia",
                          "Olympia", "California", "Hua", "Ion", "Nevada", "Maria", "Iti", "Anna", "Laser"}

        return fam_set, species_set, lat_fam_set, lat_genus_set


def _check_sentences(sent, plant_set):
    """
    Return true if any of the plant names from gazetteers is found within sentence.
    :param sent: str sentence from Text+Berg XML input file
    :param plant_set: set of plant names
    :return: boolean True if sentence substring matches any of the set's names
    """
    # also add spaces to ensure that tokens are considered
    if any(" {} ".format(plant_name) in sent for plant_name in plant_set):
        return True
    else:
        return False


def _sent_is_noisy(sent):
    """
    Check if sentences are excessively long or too short.
    :param sent: (str) sentence
    :return: bool
    """
    if len(sent.split(" ")) > 70 or len(sent.split(" ")) < 4:
        return True
    else:
        return False


def main():
    PATH_IN = "./../TextBerg/SAC/"
    PATH_OUT = "./subset_TextBerg_sentences.txt"
    PATH_GAZ = './../../resources/gazetteers/'
    default_language = "de"

    parser = argparse.ArgumentParser(
        description='Retrieve subset of sentences from T+B corpus containing plant names.')

    parser.add_argument(
        '-i', '--input_dir',
        type=str,
        default=PATH_IN,
        help='input directory containing xml files')

    parser.add_argument(
        '-o', '--output_file',
        type=str,
        default=PATH_OUT,
        help='output file containing subselection of sentences')

    parser.add_argument(
        '-g', '--gazetteers',
        type=str,
        default=PATH_GAZ,
        help='path to gazetteer files')

    parser.add_argument(
        '-l', '--language',
        type=str,
        default=default_language,
        help='language iso code {de, en}')

    args = parser.parse_args()
    PATH_IN = args.input_dir
    PATH_OUT = args.output_file
    PATH_GAZ = args.gazetteers
    language = args.language

    files = sorted([file for file in os.listdir(PATH_IN) if file.endswith("{}.xml".format(language))])

    vern_fam, vern_species, lat_fam, lat_species = _load_gazetteers(PATH_GAZ, language)

    with open(PATH_OUT, 'w', encoding='utf-8') as outfile:
        for file in files:
            year = file[13:17]
            print("# Processing year {}".format(year), file=sys.stderr, flush=True)
            with open(PATH_IN + file, 'rb') as infile:
                sent_iterator = _parse_xml(infile)
                for sent in sent_iterator:
                    FOUND = False
                    for single_set in vern_fam, vern_species, lat_fam:  # , lat_species:
                        if _check_sentences(sent, single_set):
                            if _sent_is_noisy(sent):
                                pass
                            else:
                                FOUND = True
                    if FOUND:
                        outfile.write(sent + "\n")
                sent_iterator.close()

    print(">> all done!", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
