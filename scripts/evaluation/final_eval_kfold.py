# usr/bin/env python2.7
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Compute average score over all folds from k-fold crossvalidation.

Take accuracy, precision, recall and f-score from last epoch .scores files of all k folds
and compute averaged final scores for each model.

How to run the code:
$ python2 final_eval_kfold.py -d ./../../evaluation/baseline_CharDim/FULL_MODEL_NAME -o ./evaluation_files/

"""
from __future__ import print_function
from collections import defaultdict
import argparse
import io
import os
import sys


def _clean_score(score):
    """
    Strip punctuation signs and return cleaned float of score.
    :param score: string with possible punctuation signs.
    :return: float
    """

    return float(score.rstrip(";").rstrip("%"))


def _get_digits(string):
    """
    Get digits from epoch scores file name.
    Example: epoch44.scores

    :param string: filename of epoch scores file
    :return: int representation of epoch number
    """
    return int(''.join(c for c in string if c.isdigit()))


def write_to_file(outfile, model_dir, no_folds, accuracy, precision, recall, f1, class_scores):
    """
    Write averaged evaluation scores to file.
    """
    outfile.write(u"# Overall scores for model {}:\n".format(model_dir))
    outfile.write(u"Average accuracy over {} folds:\t{:.2f}\n".format(no_folds, sum(accuracy) / len(accuracy)))
    outfile.write(
        u"Average precision over {} folds:\t{:.2f}\n".format(no_folds, sum(precision) / len(precision)))
    outfile.write(u"Average recall over {} folds:\t{:.2f}\n".format(no_folds, sum(recall) / len(recall)))
    outfile.write(u"Average f1 over {} folds:\t{:.2f}\n".format(no_folds, sum(f1) / len(f1)))
    outfile.write(u"\n# Overall scores per class for model {}: \n".format(model_dir))
    for class_name, scores in sorted(class_scores.items()):
        outfile.write(class_name + u"\n")
        for score in scores.items():
            outfile.write(u"\t Score {}: {:.2f}".format(score[0], score[1] / no_folds) + "\n")


def main():
    PATH = "/./../Evaluation/baseline_CharDim/model_CharDim/"

    parser = argparse.ArgumentParser(description='Compute final evaluation scores')

    parser.add_argument(
        '-d', '--directory',
        type=str,
        default=PATH,
        help='directory name to evaluate over k-folds')
    
    parser.add_argument(
        '-o', '--outdir',
        type=str,
        default='./',
        help='output directory for averaged evaluation')

    args = parser.parse_args()
    directory = args.directory
    OUT_DIR = args.outdir

    print("Performing evaluation for model: {}".format(directory), file=sys.stderr)
    model_dir = str(directory)
    left_index = model_dir.find("char_dim=")
    end_index = model_dir.find("/", left_index)
    shortened_model_name = model_dir[left_index:end_index]
    print("Shortened model name: {}".format(shortened_model_name), file=sys.stderr)

    no_folds = 0
    accuracy, precision, recall, f1 = [], [], [], []
    class_scores = defaultdict(dict)
    print(model_dir)
    for subdir, fold_dirs, files in os.walk(model_dir):
        for fold_dir in sorted(fold_dirs):
            epoch_numbers = []
            if fold_dir == ".DS_Store":
                continue

            print("Processing model fold: {}".format(fold_dir), file=sys.stderr)
            no_folds += 1
            file_list = []

            FOLD_PATH = os.path.join(model_dir, fold_dir)
            for file in sorted(os.listdir(FOLD_PATH)):
                epoch_numbers.append(_get_digits(file))
                file_list.append(file)

            highest_epoch = [file for file in file_list if str(max(epoch_numbers)) in file][1]

            FILE_PATH = os.path.join(FOLD_PATH, highest_epoch)
            print("Last epoch file: {}".format(highest_epoch), file=sys.stderr)
            with open(FILE_PATH, 'r') as last_epoch_scores:
                lines = last_epoch_scores.readlines()
                acc, acc_score, prec, prec_score, rec, rec_score, fb, f_score = lines[1].split()

                # overall scores for each fold
                accuracy.append(_clean_score(acc_score))
                precision.append(_clean_score(prec_score))
                recall.append(_clean_score(rec_score))
                f1.append(_clean_score(f_score))

                for line in lines[2:]:
                    # scores per class for each fold
                    plant_class, prec, prec_score, rec, rec_score, fb, f_score, entities = line.split()

                    try:
                        class_scores[plant_class][prec] += _clean_score(prec_score)
                        class_scores[plant_class][rec] += _clean_score(rec_score)
                        class_scores[plant_class][fb] += _clean_score(f_score)
                    except KeyError:
                        class_scores[plant_class][prec] = 0
                        class_scores[plant_class][rec] = 0
                        class_scores[plant_class][fb] = 0

                        class_scores[plant_class][prec] += _clean_score(prec_score)
                        class_scores[plant_class][rec] += _clean_score(rec_score)
                        class_scores[plant_class][fb] += _clean_score(f_score)

        with io.open(OUT_DIR+"eval_{}".format(shortened_model_name), "w", encoding='utf-8') as outfile:
            write_to_file(outfile, model_dir, no_folds, accuracy, precision, recall, f1, class_scores)


if __name__ == "__main__":
    main()
