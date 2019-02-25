# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Generate possible Latin variants for database.

Example:
    Dünnästiger Pippau	Crepis capillaris (L.) Wallr.
    Dünnästiger Pippau	Crepis capillaris

    Mauer-Habichtskraut	Hieracium murorum L.
    Mauer-Habichtskraut	Hieracium murorum

    Dreizähniges Habichtskraut	Hieracium laevigatum Willd.
    Dreizähniges Habichtskraut	Hieracium laevigatum

How to run the code:
$ python3 add_variants_database.py -i ./../../resources/gazetteers/lookup_table/de_lat_lookup.tsv -o ./outfile

"""
import argparse
import sys


def main():
    PATH_IN = "./../../resources/gazetteers/lookup_table/en_lat_referencedatabase.txt"
    PATH_OUT = "./../../resources/gazetteerslookup_table/en_lat_referencedatabase_variants.txt"

    parser = argparse.ArgumentParser(
        description='Add variants to reference database file.')

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

    with open(PATH_IN, "r") as infile, open(PATH_OUT, "w") as outfile:
        print(">> processing input file: {}\n>> writing to output file {}".format(infile.name, outfile.name),
              file=sys.stderr, flush=True)
        for line in infile:
            line = line.rstrip("\n")
            de, lat = line.split("\t")
            outfile.write("{}\t{}\n".format(de, lat))
            try:
                if len(lat.split(" ")) > 2:
                    species, epithet, *rest = lat.split(" ")
                    if epithet != "x":
                        outfile.write("{}\t{} {}\n".format(de, species, epithet))
                    else:
                        outfile.write("{}\t{}\n".format(de, lat))
            except ValueError:
                outfile.write("{}\t{}\n".format(de, lat))

    print(">> all done!", file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
