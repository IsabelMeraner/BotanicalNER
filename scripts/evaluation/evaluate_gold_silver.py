# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Evaluate automatically annnotated silver standard against manually corrected gold standard.

How to run the code:
$ python3 evaluate_gold_silver.py -s ./../../resources/corpora/gold_standard/de/alldata.test.fold1SILVER_de.txt 
   -g ./../../resources/corpora/gold_standard/de/alldata.test.fold1GOLD_de.txt

"""
import argparse
import sys
from collections import defaultdict


def _split_line(line):
    """
    Split line at tabs.
    :param line: str containing TOKEN\tLEMMA\tPOS\tIOB
    :return: line_split (list of items per line)
    """
    try:
        line_split = line.rstrip("\n").split("\t")
    except ValueError:  # newline
        pass

    if line_split:
        return line_split


def get_counts(iob_gold, iob_silver, tn, tp, fn, matching_dict, fp_from_tag1_to_tag2, non_matching_tags,
               fp_from_tag_to_O):
    """
    Count tp, tn, fp, fn of silverstandard file.
    :return: tn, tp, fn, matching_dict, fp_from_tag1_to_tag2, non_matching_tags, fp_from_tag_to_O
    """
    # check for missing tags in files
    if iob_gold == "" or iob_silver == "":
        raise ValueError("Empty IOB tags are not allowed in input file")

    if iob_silver == 'O' and iob_gold == 'O':
        tn += 1

    if iob_silver != 'O' and iob_gold != 'O':
        if iob_silver == iob_gold:
            tp += 1
            matching_dict[iob_silver] += 1
        else:
            fp_from_tag1_to_tag2 += 1
            non_matching_tags += 1

    else:
        if iob_silver == "O" and iob_gold != "O":
            fn += 1
            non_matching_tags += 1
        elif iob_silver != "O" and iob_gold == "O":
            fp_from_tag_to_O += 1
            non_matching_tags += 1

    return tn, tp, fn, matching_dict, fp_from_tag1_to_tag2, non_matching_tags, fp_from_tag_to_O


def main():
    SILVER = "./../../resources/corpora/gold_standard/de/alldata.test.fold1SILVER_de.txt"
    GOLD = "./../../resources/corpora/gold_standard/de/alldata.test.fold1GOLD_de.txt"

    parser = argparse.ArgumentParser(
        description='Evaluate silver against gold standard.')

    parser.add_argument(
        '-s', '--silver_file',
        type=str,
        default=SILVER,
        help='automatically annotated silver standard')

    parser.add_argument(
        '-g', '--gold_file',
        type=str,
        default=GOLD,
        help='manually corrected gold standard')

    args = parser.parse_args()
    silver_file = args.silver_file
    gold_file = args.gold_file

    tp = 0
    non_matching_tags = 0
    fn = 0
    fp_from_tag_to_O = 0
    fp_from_tag1_to_tag2 = 0
    tn = 0

    matching_dict = defaultdict(int)

    tokens_counter = 0
    check_set_classes = set()
    with open(silver_file, "r") as silver, open(gold_file, "r") as gold:
        for line_silver, line_gold in zip(silver, gold):
            try:
                token_silver, lemma_silver, pos_silver, iob_silver = _split_line(line_silver)
                token_gold, lemma_gold, pos_gold, iob_gold = _split_line(line_gold)
                tokens_counter += 1
            except ValueError:
                #print(line_silver, line_gold)
                continue

            check_set_classes.add(iob_gold)
            check_set_classes.add(iob_silver)

            tn, tp, fn, matching_dict, fp_from_tag1_to_tag2, non_matching_tags, fp_from_tag_to_O = get_counts(iob_gold,
                                                                                                              iob_silver,
                                                                                                              tn, tp,
                                                                                                              fn,
                                                                                                              matching_dict,
                                                                                                              fp_from_tag1_to_tag2,
                                                                                                              non_matching_tags,
                                                                                                              fp_from_tag_to_O)

    # perc_matching = (tp/tokens_counter) * 100
    # per_nonmatching = (non_matching_tags/tokens_counter) * 100

    acc = (tp + tn) / (tp + tn + fp_from_tag1_to_tag2 + fp_from_tag_to_O + fn) * 100
    prec = tp / (tp + fp_from_tag_to_O + fp_from_tag1_to_tag2) * 100
    rec = tp / (tp + fn) * 100
    f1 = ((2 * tp) / ((2 * tp) + (fp_from_tag_to_O + fp_from_tag1_to_tag2) + fn)) * 100

    print(20 * "-", file=sys.stderr, flush=True)
    print("Found {} lines".format(tokens_counter), file=sys.stderr, flush=True)
    print("Accuracy: {:.2f}%\nPrecision: {:.2f}%\nRecall: {:.2f}%\nF1: {:.2f}%".format(acc, prec, rec, f1),
          file=sys.stderr, flush=True)
    print("Found {} unique classes of IOB-tags:\n{}".format(len(check_set_classes), check_set_classes), file=sys.stderr,
          flush=True)
    print(20 * "-", file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
