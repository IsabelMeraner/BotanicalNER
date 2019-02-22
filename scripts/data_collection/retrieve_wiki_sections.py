# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Parse Wikipedia abstracts from API.
source = https://www.mediawiki.org/wiki/API:Main_page (Date accessed: 17.07.18)

Retrieve Wikipedia abstracts for plant names.

How to run the code:
$ python3 retrieve_wiki_sections.py -i ./../../resources/gazetteers/lat/lat_species.txt
  -t ./outfile_trivialsections.txt -a outfile_wikiabstracts.txt -l de


"""

import argparse
import sys
import wikipediaapi


def check_page(page_py):
    """
    Returns true if the page exists.
    :param page_py:
    :return: boolean
    """
    try:
        if page_py.exists():
            return True
    except:
        pass


def get_trivial_names_secvtion(sections, outfile):
    """
    Retrieve trivial name sections from Wiki page.
    :param sections: (iterable) list of section names
    :param outfile: (file-like obj) trivial names outfile
    """
    for s in sections:
        if "Etymology" in s.title or "Common names" in s.title:
            outfile.write(s.text + "\n\n\n")


def main():
    PATH_IN = "./../../resources/gazetteers/lat/lat_species.txt"
    OUTFILE_TRIVIAL = "./wiki_trivialnames_en.txt"
    OUTFILE_ABSTRACTS = "./wiki_abstracts_en.txt"
    default_language = "de"

    parser = argparse.ArgumentParser(
        description='Retrieve wiki articles.')

    parser.add_argument(
        '-i', '--input_file',
        type=str,
        default=PATH_IN,
        help='input gazetteer file with Latin names')

    parser.add_argument(
        '-t', '--trivial_file',
        type=str,
        default=OUTFILE_TRIVIAL,
        help='output file with retrieved trivial names')

    parser.add_argument(
        '-a', '--abstracts_file',
        type=str,
        default=OUTFILE_ABSTRACTS,
        help='output file with retrieved abstracts')

    parser.add_argument(
        '-l', '--language',
        type=str,
        default=default_language,
        help='language for Wikipedia APII {de, en}')

    args = parser.parse_args()
    PATH_IN = args.input_file
    PATH_TRIVIAL = args.trivial_file
    PATH_ABSTRACTS = args.abstracts_file
    language = args.language

    wiki_wiki = wikipediaapi.Wikipedia(language)

    with open(PATH_IN, "r") as infile, open(PATH_ABSTRACTS, "w", encoding="utf-8") as abstracts, \
            open(PATH_TRIVIAL, "w", encoding="utf-8") as trivial:
        print(">> retrieving wiki abstracts and trivial name sections for name list {}".format(infile.name),
              file=sys.stderr, flush=True)
        for line in infile:
            line = line.rstrip("\n").rstrip(" ")
            try:
                names = line.split(" ")
                title = "_".join(names)
            except ValueError:
                title = line

            page_py = wiki_wiki.page(title)
            if check_page(page_py):
                # write abstract to file
                abstracts.write(page_py.summary + "\n\n\n")

                # write trivial name sections to file
                # get_trivial_names_secvtion(page_py.sections, trivial, level=0)

    print(">> all done!", file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
