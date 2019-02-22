# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019


"""
Parse Darwin core archives into tab-separated format.
source = http://www.catalogueoflife.org/DCA_Export/index.php (Date accessed: 17.07.18)

The catalogue of life contains systematic information about each taxon as well as vernacular names in several languages.

# Tabular data structure
scientificName	kingdom	phylum	class	order	superfamily	family	genericName	genus	subgenus	specificEpithet	infraspecificEpithet	scientificNameAuthorship

# Inconsistent handling of language identifiers in CoL-archives:
taxonID	    vernacularName	    language
11769839	grassflower	        English             # German
18158011	Pond Cypress	    Eng                 # Ger

--> if no language tag is given, use langid-module for automatic, character-based language identification

How to run the code:
$ python3 extracttaxa_cat_of_life -t ./colarchive/taxa/ -v ./colarchive/vernacular/ -l ./latin.out
 -d ./german.out -e ./english.out -r rest_vernacular.out

"""

import argparse
import langid
import sys
from os import listdir


def _write_to_file(set, outfile):
    for item in set:
        if item == "":
            continue
        else:
            outfile.write(item + "\n")


def _get_scientific_names(files_taxa, PATH_TAXA):
    """
    Parse darwin core archive from Cat. of Life database and retrieve Latin plant names.
    :param files_taxa: (iterable) list of taxa files
    :param PATH_TAXA: (str) file path for taxa files
    :return: scientific_names, kingdom, phylum, class_plants, order, family, genus (set structure of Latin names)
    """
    scientific_names = set()
    kingdom = set()
    phylum = set()
    class_plants = set()
    order = set()
    family = set()  # superfamily + family
    genus = set()  # genericName + genus + subgenus

    for file in files_taxa:
        print("#### Processing FILE [TAXA]: {}".format(file), file=sys.stderr, flush=True)
        with open(PATH_TAXA + file, "r", encoding="utf-8") as infile:
            for line in infile:
                if line.startswith("taxonID") or line.startswith("\ufefftaxonID"):
                    continue
                else:
                    data = line.split("\t")
                    scientific_names.add(data[9])
                    kingdom.add(data[10])
                    phylum.add(data[11])
                    class_plants.add(data[12])
                    order.add(data[13])
                    family.add(data[14])
                    family.add(data[15])
                    genus.add(data[16])
                    genus.add(data[17])

    return scientific_names, kingdom, phylum, class_plants, order, family, genus


def _get_vernacular_names(files_vern, PATH_VERN):
    """
    Parse darwin core archive from Cat. of Life database and retrieve vernacular plant names.
    :param files_vern: (iterable) list of vernacular files
    :param PATH_VERN: (str) file path for vernacular files
    :return: vernacular_names_de, vernacular_names_en, vernacular_names_withoutlanguagetag_final
              (set structure for vernacular names)
    """
    vernacular_names_en = set()
    vernacular_names_de = set()
    vernacular_names_withoutlanguagetag = set()
    vernacular_names_withoutlanguagetag_final = set()

    for file in files_vern:
        print("#### Processing FILE [VERNACULAR]: {}".format(file), file=sys.stderr, flush=True)
        with open(PATH_VERN + file, "r", encoding="utf-8") as infile:
            for line in infile:
                if line.startswith("taxonID"):
                    continue
                data = line.split("\t")
                if data[2] == "Eng" or data[2] == "English":  # inconsistent handling of language identifiers
                    vernacular_names_en.add(data[1])
                elif data[2] == "Ger" or data[2] == "German":
                    vernacular_names_de.add(data[1])
                elif data[2] == "":
                    vernacular_names_withoutlanguagetag.add(data[1])

            for name in vernacular_names_withoutlanguagetag:
                lang = langid.classify(name)
                if lang[0] == "en":
                    vernacular_names_en.add(name)
                elif lang[0] == "de" and name[0].isupper():  # isupper to avoid adding Japanese (?) common names
                    vernacular_names_de.add(name)
                else:
                    vernacular_names_withoutlanguagetag_final.add(name)

    return vernacular_names_de, vernacular_names_en, vernacular_names_withoutlanguagetag_final


def main():
    PATH_TAXA = "./../catalogueofLife_plantae_de-en-lat/taxa/"
    PATH_VERN = "./../catalogueofLife_plantae_de-en-lat/vernacular/"

    parser = argparse.ArgumentParser(
        description='Retrieve scientific and vernacular names from Cat. of Life darwin core archive.')

    parser.add_argument(
        '-t', '--taxa_dir',
        type=str,
        default=PATH_TAXA,
        help='input directory with tabular taxa files')

    parser.add_argument(
        '-v', '--vern_dir',
        type=str,
        default=PATH_VERN,
        help='input directory with tabular vernacular name files')

    parser.add_argument(
        '-l', '--latin_out',
        type=str,
        default="./latin_CoL_outfile.txt",
        help='outfile containing Latin names extracted from Cat. of Life')

    parser.add_argument(
        '-d', '--de_out',
        type=str,
        default="./german_CoL_outfile.txt",
        help='outfile containing German names extracted from Cat. of Life')

    parser.add_argument(
        '-e', '--en_out',
        type=str,
        default="./english_CoL_outfile.txt",
        help='outfile containing English names extracted from Cat. of Life')

    parser.add_argument(
        '-r', '--rest_out',
        type=str,
        default="./restvernnames_CoL_outfile.txt",
        help='outfile containing remaining vernacular names extracted from Cat. of Life')

    args = parser.parse_args()
    PATH_TAXA = args.taxa_dir
    PATH_VERN = args.vern_dir
    PATH_OUT_VERN_DE = args.de_out
    PATH_OUT_VERN_EN = args.en_out
    PATH_OUT_VERN_X = args.rest_out
    PATH_OUT_LATIN = args.latin_out

    files_taxa = [f for f in listdir(PATH_TAXA) if f.endswith(".txt")]
    files_vern = [f for f in listdir(PATH_VERN) if f.endswith(".txt")]

    scientific_names, kingdom, phylum, class_plants, order, family, genus = _get_scientific_names(files_taxa, PATH_TAXA)

    with open(PATH_OUT_LATIN, "a", encoding="utf-8") as outfile:
        _write_to_file(scientific_names, outfile)
        _write_to_file(kingdom, outfile)
        _write_to_file(phylum, outfile)
        _write_to_file(class_plants, outfile)
        _write_to_file(order, outfile)
        _write_to_file(family, outfile)
        _write_to_file(genus, outfile)

    # print("# Scientific names: \n", scientific_names, file=sys.stderr, flush=True)
    # print("# Kingdom names: \n", kingdom, file=sys.stderr, flush=True)
    # print("# Phylum names: \n", phylum, file=sys.stderr, flush=True)
    # print("# Class names: \n", class_plants, file=sys.stderr, flush=True)
    # print("# Order names: \n", order, file=sys.stderr, flush=True)
    # print("# Family names: \n", family, file=sys.stderr, flush=True)
    # print("# Genus names: \n", genus, file=sys.stderr, flush=True)

    vernacular_names_de, vernacular_names_en, vernacular_names_withoutlanguagetag_final = _get_vernacular_names(
        files_vern, PATH_VERN)

    with open(PATH_OUT_VERN_DE, "a", encoding="utf-8") as outfile_de, \
            open(PATH_OUT_VERN_EN, "a", encoding="utf-8") as outfile_en, \
            open(PATH_OUT_VERN_X, "a", encoding="utf-8") as outfile_x:
        _write_to_file(vernacular_names_en, outfile_en)
        _write_to_file(vernacular_names_de, outfile_de)
        _write_to_file(vernacular_names_withoutlanguagetag_final, outfile_x)

    # print("# Vernacular names de:\n", vernacular_names_de, file=sys.stderr, flush=True)
    # print("# Vernacular names en:\n", vernacular_names_en, file=sys.stderr, flush=True)
    # print("# Vernacular names (others):\n", vernacular_names_withoutlanguagetag_final, file=sys.stderr, flush=True)

    print(">> all done!", file=sys.stderr, flush=True)

if __name__ == '__main__':
    main()
