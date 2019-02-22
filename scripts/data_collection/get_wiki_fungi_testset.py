# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Parse Wikipedia article abstracts from API.
API information = https://www.mediawiki.org/wiki/API:Main_page (Date accessed: 17.07.18)

Query category of animals, fungi for in-domain testing on held-out entity instances.

How to run the code:
$ python3 get_wiki_fungi_testset.py -o ./outfile.txt -c Pilze -l de

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


def main():
    PATH_OUT = "./../../resources/corpora/de/test_set_fungi.txt"
    default_category = "Pilze" # 'Liste_der_Gefäßpflanzen_Deutschlands'
    default_language = "de"

    parser = argparse.ArgumentParser(
        description='Parse wiki category to retrieve sentences about fungi.')

    parser.add_argument(
        '-o', '--output_file',
        type=str,
        default=PATH_OUT,
        help='output file with fungi sentences')

    parser.add_argument(
        '-c', '--category',
        type=str,
        default=default_category,
        help='category {fungi, boletales, agaricales}')

    parser.add_argument(
        '-l', '--language',
        type=str,
        default=default_language,
        help='language for Wikipedia APII {de, en}')

    args = parser.parse_args()
    PATH_OUT = args.output_file
    category = args.category
    language = args.language

    wiki_wiki = wikipediaapi.Wikipedia(language)

    if language == "de":
        CAT = "Kategorie:{}".format(category)
    elif language == "en":
        CAT = "Category:{}".format(category)
    else:
        raise NotImplementedError("Choose a language iso-code {de|en}")

    with open(PATH_OUT, "w", encoding="utf-8") as abstracts:
        cat = wiki_wiki.page(CAT)
        entity_names = []

        for name, _ in cat.categorymembers.items():
            if not name.startswith(CAT[:7]) and not name == category:
                entity_names.append(name)
        print(">> Retrieving abstracts from pages:\n{}".format(entity_names), file=sys.stderr, flush=True)

        for e_name in entity_names:
            page_py = wiki_wiki.page(e_name)
            abstracts.write(page_py.summary + "\n\n")


if __name__ == "__main__":
    main()
