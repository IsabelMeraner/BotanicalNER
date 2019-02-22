# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Add the most important morphological variants for German:
- gewächse | -Gewächse      -> Gewächsen, Gewächs, Gewächses
- blütler | blüthler        -> Blütlern, Blütlers

How to run the code:
$ python3 add_german_variants.py -i ./../../resources/gazetteers/de/de_fam.txt -o ./outfile.txt


"""
import sys
import argparse

def main():

    PATH_IN = "./../../resources/gazetteers/de/de_fam.txt"
    PATH_OUT = "./../../resources/gazetteers/de/de_fam_variants.txt"

    parser = argparse.ArgumentParser(
        description='Add German variants to gazetteer file.')

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

    with open(PATH_IN, 'r') as infile, open(PATH_OUT, 'w', encoding='utf-8') as outfile:
        print(">> processing input file: {}\n>> writing to output file {}".format(infile.name, outfile.name),
              file=sys.stderr, flush=True)
        for line in infile:
            line = line.rstrip("\n")

            if line == "\n":
                continue
            else:
                if line.endswith("-Gewächse"):
                    outfile.write(line +"\n")
                    outfile.write(line +"n\n")

                    line = line.replace("-Gewächse", "-Gewächs")
                    outfile.write(line +"\n")
                    outfile.write(line +"es\n")


                elif line.endswith("gewächse"):
                    outfile.write(line + "\n")
                    outfile.write(line + "n\n")

                    line = line.replace("gewächse", "gewächs")
                    outfile.write(line + "\n")
                    outfile.write(line + "es\n")

                elif line.endswith("blütler"):
                    outfile.write(line + "\n")
                    outfile.write(line + "n\n")
                    outfile.write(line + "s\n")

                elif line.endswith("blüthler"):
                    outfile.write(line + "\n")
                    outfile.write(line + "n\n")
                    outfile.write(line + "s\n")

                else:
                    outfile.write(line + "\n")

    print(">> all done!", file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
