# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Perform final checking of gazetteers and adding of plant lists:

-> check that for every plant name, every possible variant is added, depending on modifier or hyphenisation:
		Gewöhnliche Zwerg-Gänsekresse
		+ Zwerg-Gänsekresse
		+ Gewöhnliche Zwerggänsekresse
		+ Zwerggänsekresse
		+ Gänsekresse

		Amerikanisches Purpurglöckchen
		+ Purpurglöckchen

How to run the code:
$ python3 add_compound_variants.py -i ./../../resources/gazetteers/de/de_species.txt -o ./outfileGAZ.txt

"""
import argparse
import sys


def _process_file(infile, outfile):
    """
    Iterate over name candidates and automatically add variants, depending on structure of name.

    :param infile: (file-like object) raw, noisy gazetteer
    :param outfile: (file-like object) cleaned gazetteer with added name variants
    """

    for line in infile:
        line = line.rstrip("\n")
        if line.startswith("#") or line == "\n":
            continue

        try:
            left, right = line.split("-")
            outfile.write(line + "\n")  # Gewöhnliche Zwerg-Gänsekresse
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
            outfile.write(line + "\n")

        try:
            adj, name = line.split(" ")
            outfile.write(line + "\n")  # Amerikanisches Purpurglöckchen
            outfile.write(name + "\n")  # Purpurglöckchen


        except ValueError:
            outfile.write(line + "\n")


def main():
    PATH_IN = "./../../resources/gazetteers/de/de_species.txt"
    PATH_OUT = "./../../resources/gazetteers/de_species_unique_out_variants.txt"

    parser = argparse.ArgumentParser(
        description='Add name variants to input gazetteer.')

    parser.add_argument(
        '-i', '--input_file',
        type=str,
        default=PATH_IN,
        help='input file (one name candidate per line)')

    parser.add_argument(
        '-o', '--output_file',
        type=str,
        default=PATH_OUT,
        help='output file with added, cleaned variants')

    args = parser.parse_args()
    PATH_IN = args.input_file
    PATH_OUT = args.output_file

    with open(PATH_IN, "r", encoding="utf-8") as infile, open(PATH_OUT, "w", encoding="utf-8") as outfile:
        print(">> processing input file: {}\n>> writing to output file {}".format(infile.name, outfile.name),
              file=sys.stderr, flush=True)

        _process_file(infile, outfile)

        print(">> all done!", file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
