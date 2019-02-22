#!/bin/bash
# author: Isabel Meraner
# original script by Nora Hollenstein (adapted version)
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019


declare -a folds=("1" "2" "3" "4" "5");

echo "STARTING CROSSVALIDATION TRAINING OF LSTM-CRF"
echo "------------------"

for f in "${folds[@]}"
  do

    echo "FOLD ${f}"

    # use theano flags to run on specific gpu
    time THEANO_FLAGS='device=cuda7,dnn.conv.algo_bwd_filter=deterministic,dnn.conv.algo_bwd_data=deterministic,dnn.include_path=/usr/include,dnn.library_path=/usr/lib/x86_64-linux-gnu,force_device=True' python2.7 train-no-dev.py --train ./../data/crossvalidation_folds/alldata/alldata.train.fold${f}.txt --test ./../data/crossvalidation_folds/alldata/alldata.test.fold${f}.txt --tag_scheme iob --zeros 1 --fold ${f} --data "alldata" --pre_emb ./../pretrained_emb_de/fasttext_germ --word_dim 300
  done

echo "ENDING CROSSVALIDATION LSTM-CRF TRAINING"
echo "ALL DONE................... ."


