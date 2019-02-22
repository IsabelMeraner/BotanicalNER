# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""

Create k-fold for crossvalidation training and evaluation.
Shuffle sentences with constant seed to guarantee reproducibility.

= Different types of combination:
    ALL_RESOURCES (5FOLD)
    SINGLE_RESOURCES (5FOLD): wiki, tb, blogs
    WIKI+T+B+BLOGS (5FOLD)
    WIKI+T+B (5FOLD)
    WIKI+BLOGS (5FOLD)
    T+B+BLOGS

# How to run the code:
$ python3 kfold_crossvalidation.py -d ./../../resources/corpora/training_corpora/de/
"""

import argparse
import os
import sys
from collections import defaultdict
import numpy as np
from sklearn.model_selection import KFold


def get_xy_data(PATH, file):
    """
    Split data into two arrays for kfold splitting.
    :param PATH: (str) input filepath
    :param file: (file-like object)
    :return: X, y (list)
    """
    EOS = "EOS"

    with open(PATH + file, 'r') as infile:
        X, y = [], []

        sentence = []
        sentence_iobtags = []
        for line in infile:
            try:
                token, lemma, tag, iob = line.rstrip("\n").split("\t")
                sentence.append([token, lemma, tag])
                sentence_iobtags.append([iob])

            except ValueError:
                sentence.append([EOS])
                sentence_iobtags.append([EOS])

                X.append(sentence[:])
                y.append(sentence_iobtags[:])

                sentence.clear()
                sentence_iobtags.clear()
        return X, y


def write_to_file(X, y, file):
    """
    Write split data to output file
    :param X: (list) containing triples of (token, lemma, tag)
    :param y: (list) containing iob-tags
    :param file: (file-like object) output file
    """
    for sentence, tags in zip(X, y):
        for triple, iob_tag in zip(sentence, tags):
            if triple[0] == "EOS":
                file.write("\n")
            else:
                token, lemma, tag = triple
                file.write("{}\t{}\t{}\t{}\n".format(token, lemma, tag, iob_tag[0]))


def kfold_splitting(PATH, X, y, output_filename, fn, singlefolds=False):
    X = np.array(X, dtype=object)
    y = np.array(y, dtype=object)

    # shuffle randomly and keep same seed for X and y array
    np.random.seed(1234)
    np.random.shuffle(X)
    np.random.seed(1234)
    np.random.shuffle(y)

    if singlefolds:
        output_filename = fn

    kf = KFold(n_splits=5)
    for fold_nr, (train_index, test_index) in enumerate(kf.split(X), start=1):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        with open(PATH + output_filename + ".train.fold{}.txt".format(fold_nr), 'w', encoding='utf-8') as outfile_train, \
                open(PATH + output_filename + ".test.fold{}.txt".format(fold_nr), 'w',
                     encoding='utf-8') as outfile_test:
            write_to_file(X_train, y_train, outfile_train)
            write_to_file(X_test, y_test, outfile_test)


def main():
    PATH = './../../resources/corpora/training_corpora/de/'

    parser = argparse.ArgumentParser(description='Apply K-fold crossvalidation')

    parser.add_argument(
        '-d', '--directory',
        type=str,
        default=PATH,
        help='pass directory with training data')

    args = parser.parse_args()
    PATH = args.directory

    out_dir = PATH + "crossvalidation_folds/"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    xy_file_storage = defaultdict(tuple)
    for file in sorted(os.listdir(PATH)):
        if file.endswith(".iob.txt"):
            fn = file[:-19]
            print(">> processing file {}".format(file), file=sys.stderr, flush=True)
            X, y = get_xy_data(PATH, file)

            # create folds for single resources
            outdir = out_dir + "single_folds/"
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            kfold_splitting(outdir, X, y, "", fn, singlefolds=True)

            xy_file_storage[fn] = (X, y)

    all_x, all_y = [], []  # ALL
    tb_blogs_x, tb_blogs_y = [], []  # TB + Blogs
    wiki_blogs_x, wiki_blogs_y = [], []  # WIKI + Blogs
    wiki_tb_x, wiki_tb_y = [], []  # WIKI + TB
    wiki_tb_blogs_x, wiki_tb_blogs_y = [], []  # WIKI + TB + Blogs

    for fn, (X, y) in xy_file_storage.items():
        all_x.extend(X)
        all_y.extend(y)

        if "plantblog" in fn:
            tb_blogs_x.extend(X)
            tb_blogs_y.extend(y)

            wiki_blogs_x.extend(X)
            wiki_blogs_y.extend(y)

            wiki_tb_blogs_x.extend(X)
            wiki_tb_blogs_y.extend(y)

        elif "TextBerg" in fn:
            tb_blogs_x.extend(X)
            tb_blogs_y.extend(y)

            wiki_tb_x.extend(X)
            wiki_tb_y.extend(y)

            wiki_tb_blogs_x.extend(X)
            wiki_tb_blogs_y.extend(y)

        elif "wiki" in fn:
            wiki_blogs_x.extend(X)
            wiki_blogs_y.extend(y)

            wiki_tb_x.extend(X)
            wiki_tb_y.extend(y)

            wiki_tb_blogs_x.extend(X)
            wiki_tb_blogs_y.extend(y)

    # create combined data set
    outdir = out_dir + "alldata/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    kfold_splitting(outdir, all_x, all_y, "alldata", "")

    # tb+blogs
    outdir = out_dir + "tb_blogs/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    kfold_splitting(outdir, tb_blogs_x, tb_blogs_y, "tb_blogs", "")

    # wiki+blogs
    outdir = out_dir + "wiki_blogs/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    kfold_splitting(outdir, wiki_blogs_x, wiki_blogs_y, "wiki_blogs", "")

    # wiki+tb
    outdir = out_dir + "wiki_tb/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    kfold_splitting(outdir, wiki_tb_x, wiki_tb_y, "wiki_tb", "")

    # wiki+tb+blogs
    outdir = out_dir + "wiki_tb_blogs/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    kfold_splitting(outdir, wiki_tb_blogs_x, wiki_tb_blogs_y, "wiki_tb_blogs", "")


if __name__ == "__main__":
    main()
