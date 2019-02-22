# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Add Latin abbreviated name variants to each input name.
Bellis perennis -> B. perennis
Lactuca sativa -> L. sativa

How to run the code:
$ python3 add_latin_abbreviations.py -i ./../../resources/gazetteers/lat/lat_species.txt -o ./outfile.txt

"""

import argparse
import sys


def main():
    PATH_IN = "./../../resources/gazetteers/lat/lat_species.txt"
    PATH_OUT = "./../../resources/gazetteers/lat/lat_species_abbreviations.txt"
    parser = argparse.ArgumentParser(
        description='Add Latin abbreviations to gazetteer file.')

    parser.add_argument(
        '-i', '--input_file',
        type=str,
        default=PATH_IN,
        help='input file (one name candidate per line)')

    parser.add_argument(
        '-o', '--output_file',
        type=str,
        default=PATH_OUT,
        help='output file with added, abbreviated variants')

    args = parser.parse_args()
    PATH_IN = args.input_file
    PATH_OUT = args.output_file

    with open(PATH_IN, "r") as gazetteer_in, open(PATH_OUT, "w", encoding="utf-8") as outfile:
        print(">> processing input file: {}\n>> writing to output file {}".format(gazetteer_in.name, outfile.name),
              file=sys.stderr, flush=True)

        for line in gazetteer_in:
            if len(line.split(" ")) == 2:
                species, epithet = line.rstrip("\n").split(" ")
                outfile.write("{}. {}\n".format(species[0].upper(), epithet))

        print(">> all done!", file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
