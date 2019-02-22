# usr/bin/env python3
# Isabel Meraner
# Project: Plant Name Recognition
# Institute of Computational Linguistics, University of Zurich


"""
Remove duplicates from single lists of plant names.
Keep spelling variants like: Ahorn, Bergahorn, Berg-Ahorn

How to run the code:
$ python3 create_gazetteers.py -i ./../../resources/gazetteers/de/de_species.txt -o outfile.txt

"""

import argparse
import sys
import os


def add_family_variants(line, outfile):
    """
    Add systematic variants to gazetteer file.
    :param line: string (line in gazetteer)
    :param outfile: (file-like obj)
    """

    if line.endswith("ceae"):
        germ_variant = line.replace("ceae", "ceen")
        outfile.write(germ_variant + "\n")
    elif line.endswith("blütler"):
        germ_variant = line.replace("blütler", "blüthler")
        outfile.write(germ_variant + "\n")
    elif line.endswith("gewächse"):
        germ_variant = line.replace("gewächse", "-Gewächse")
        outfile.write(germ_variant + "\n")
    elif line.endswith("familie"):
        germ_variant = line.replace("familie", "-Familie")
        outfile.write(germ_variant + "\n")


def add_species_variants(line, outfile):
    """
    Add systematic variants to gazetteer file.
    :param line: string (line in gazetteer)
    :param outfile: (file-like obj)
    """

    if line.endswith("moos"):
        germ_variant = line.replace("moos", "moose")
        outfile.write(germ_variant + "\n")
    elif line.endswith("farn"):
        germ_variant = line.replace("farn", "farne")
        outfile.write(germ_variant + "\n")

    elif line.endswith("flechte"):
        germ_variant = line.replace("flechte", "flechten")
        outfile.write(germ_variant + "\n")

    try:
        left, right = line.split("-")
        outfile.write(right + "\n")  # Gänsekresse
        joined = left + right.lower()
        outfile.write(joined + "\n")  # Gewöhnliche Zwerggänsekresse
        try:
            adj, name = left.split(" ")
            joined = name + "-" + right
            joined2 = name + right.lower()
            outfile.write(joined + "\n")  # Zwerg-Gänsekresse
            outfile.write(joined2 + "\n")  # Zwerggänsekresse
        except:
            pass

    except ValueError:
        pass

    try:
        adj, name = line.split(" ")
        outfile.write(name + "\n")  # Purpurglöckchen


    except ValueError:
        pass


def add_species_english(line, outfile):
    try:
        adj, *middle, name = line.split(" ")  # scrub cypress pine
        outfile.write(name + "\n")
    except:
        pass


def add_families_italian(line, outfile):
    if line.endswith("ceae"):
        it_variant = line.replace("ceae", "cee")
        outfile.write(it_variant + "\n")


def add_species_italian(line, outfile):
    try:
        name, *middle, adj = line.split(" ")  # Achillea moscata, Abete bianco
        outfile.write(name + "\n")
    except:
        pass


def add_species_latin(line, outfile):
    try:
        species, epithet, *rest = line.split(" ")  # Cedronella canariensis syn. Triphylla
        outfile.write(species + " " + epithet + "\n")
    except:
        pass


def main():
    PATH_IN = "./../../resources/gazetteers/de/de_species.txt"
    PATH_OUT = "./../../resources/gazetteers/de_species_unique_out_variants.txt"

    parser = argparse.ArgumentParser(
        description='Add variants to gazetteer file.')

    parser.add_argument(
        '-i', '--input_file',
        type=str,
        default=PATH_IN,
        help='input file (one name candidate per line) with tabseparated Latin names')

    parser.add_argument(
        '-o', '--output_file',
        type=str,
        default=PATH_OUT,
        help='output file with added variants')

    args = parser.parse_args()
    PATH_IN = args.input_file
    PATH_OUT = args.output_file

    names = set()

    with open(PATH_IN, "r", encoding="utf-8") as infile, open(PATH_OUT, "w", encoding="utf-8") as outfile_unique:
        print(">> processing input file: {}\n>> writing to output file {}".format(infile.name, outfile_unique.name),
              file=sys.stderr, flush=True)
        for line in infile:
            if line == "\n" or line.startswith("#"):
                continue
            else:
                line = line.rstrip("\n").lstrip(" ").rstrip(" ")
                names.add(line)

        for name in names:
            outfile_unique.write(name + "\n")

            # uncomment this line, if German family name_variants are being processed
            # add_family_variants(name, outfile_unique)

            # uncomment this line to add german name variants
            # add_species_variants(name, outfile_unique)

            # uncomment this line to add english name variants
            # add_species_english(name, outfile_unique)

            # uncomment this line to add italian family name variants
            # add_families_italian(name, outfile_unique)

            # uncomment this line to add italian species name variants
            # add_species_italian(name, outfile_unique)

            # uncomment this line to add latin species names (only species name + epithet
            # add_species_latin(name, outfile_unique)


if __name__ == '__main__':
    main()
