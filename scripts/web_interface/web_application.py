# usr/bin/env python3
# Isabel Meraner
# Project: Plant Name Recognition
# Institute of Computational Linguistics, University of Zurich


"""
Web-application to input text and highlight NER-tagged plant names.

Pipeline:
    1. input text
    2. tokenize input
    3. run tagger.py (from Lample et al. (2016))
    4. run entity_linker.py to link the detected entities to reference database (Catalogue of Life)
    5. highlight found entities and display link to database entry
"""
from flask import Flask, render_template, request
from nltk import word_tokenize
from nltk.tokenize import sent_tokenize
import subprocess
import json
import spacy
import sys
import time



def tokenize_input(inputText, language):
    """
    Use language-specific tokenizer to process and tokenize input text.
    Check for the presence of botanical abbreviations and re-merge sentences.
    :param inputText: (str) user input text from web-interface.
    :param language: (str) language to process, "de" or "en"
    """

    if language == 'de':
        sent_tokenize_list = sent_tokenize(inputText, 'german')
    elif language == 'en':
        nlp = spacy.load('en')
        sent_tokenize_list = sent_tokenize(inputText)
    else:
        raise NotImplementedError("Please choose one of the following languages (de, en).", file=sys.stderr, flush=True)

    # fix erroneous sentence segmentation
    fixed_sentences = []
    for i, sent in enumerate(sent_tokenize_list):
        if sent_tokenize_list[i].split()[-1] in ["var.", "convar.", "agg.", "ssp.", "sp.", "subsp.", "x.", "L.",
                                                 "auct.", "comb.", "illeg.", "cv.", "emend.", "al.", "f.", "hort.",
                                                 "nm.", "nom.", "ambig.", "cons.", "dub.", "superfl.", "inval.", "nov.",
                                                 "nud.", "rej.", "nec.", "nothosubsp.", "p.", "hyb.", "syn.", "synon."]:
            fixed_sentences.append(sent_tokenize_list[i] + " " + sent_tokenize_list[i + 1])
            del sent_tokenize_list[i + 1]
        else:
            fixed_sentences.append(sent)

    tokenized_input = []
    counter_abbreviations = 0
    for sent in fixed_sentences:
        if language == 'de':
            tokens = word_tokenize(sent, 'german')
        elif language == 'en':
            tokens = list(nlp(sent))

        fixed_tokens = []
        for i, token in enumerate(tokens):
            if str(tokens[i]) in ["var", "convar", "agg", "ssp", "sp", "subsp", "x", "L", "auct", "comb", "illeg", "cv",
                             "emend", "al", "f", "hort", "nm", "nom", "ambig", "cons", "dub", "superfl", "inval", "nov",
                             "nud", "rej", "nec", "nothosubsp", "p", "hyb", "syn", "synon"]:
                counter_abbreviations +=1
                fixed_tokens.append(str(tokens[i]) + ".")
                del tokens[i + 1]
            else:
                fixed_tokens.append(str(token))

        tokens_string = " ".join(fixed_tokens) + "\n"
        tokenized_input.append(tokens_string)
    tokenized_response = " ".join(tokenized_input)
    tokenized_response = tokenized_response.replace("\n ", "\n")
    print(">> Done! Remerged {} sentence(s) at botanical abbreviations".format(counter_abbreviations), file=sys.stderr, flush=True)

    with open("./output/input_tokenized.txt", "w", encoding="utf-8") as tok_file:
        tok_file.write(tokenized_response)


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=['POST'])
def get_response():
    inputText = request.form.get('data')
    language = request.form.get('lang')
    print(">> RECEIVED USER INPUT:\n {}".format(inputText), file=sys.stderr, flush=True)
    print(">> INPUT LANGUAGE: '{}'".format(language), file=sys.stderr, flush=True)

    # TOKENIZE
    if language == 'de':
        print("\n>> tokenizing German input text...")
        tokenize_input(inputText, language)
        model = "model_wiki_de"
    else:
        print("\n>> tokenizing English input text...")
        tokenize_input(inputText, language)
        model = "model_wiki_en"

    # TAGGING
    print("\n>> tagging tokenized input text...", file=sys.stderr, flush=True)
    subprocess.call(
        "python2.7 ./tagger-master/tagger.py -m ./models/{} -i ./output/input_tokenized.txt -o ./output/output_tagged.txt -d __".format(
            model), shell=True)

    # LINKING: entity_linker.py
    print("\n>> linking entity candidates to reference database", file=sys.stderr, flush=True)
    subprocess.call(
        "python3 ./entity_linker.py -i ./output/output_tagged.txt -o ./static/output_linked.json --language {}".format(
            language), shell=True)

    # JSON FILE CREATION
    print("\n>> creating json-file...", file=sys.stderr, flush=True)
    with open("./static/output_linked.json", "r") as linked_output:
        data = json.load(linked_output)
        return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")


if __name__ == "__main__":
    app.run()
