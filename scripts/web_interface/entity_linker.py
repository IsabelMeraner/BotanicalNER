# usr/bin/env python3
# author: Isabel Meraner
# Project: Neural Entity Recognition for Scientific and Vernacular Plant Names (MA-Thesis)
# Institute of Computational Linguistics (University of Zurich), 2019

"""
Entity Linking:
Link candidate entities in text to identifier in botanical reference database (Catalogue of Life [Roskov et al., 2018])
Store the linking information in a JSON-file.

Botanical Database:
- CoL: http://catalogueoflife.org/

Input:
- file generated from the script tagger.py based on the trained LSTM-CRF models (Lample et al. 2016)
  example sentence from output.txt:
  Most__O Angelonia__B-lat_genus species__O can__O be__O found__O in__O Northeastern__O Brazil__O .__O

# How to run the code:
$ python3 entity_linker.py -i ./../../resources/corpora/training_corpora/de/botlit_corpus_de.tok.pos.iob.txt
  -o ./json_file.json -f IOB -r ./../../resources/gazetteers/lookup_table/de_lat_lookup.tsv -l True
"""
from collections import defaultdict
import argparse
import json
import requests
import sys
import time


def get_bibref_information(data):
    """
    Catch KeyError when a genus rank name is queried and no bibliographic information can be retrieved.
    :param data: dictionary structure returned from API
    :return: bib_ref: bibliographic reference information from API
    """
    try:
        bib_ref = data["results"][0]["accepted_name"]["bibliographic_citation"]

    except KeyError:
        bib_ref = ""
    return bib_ref


def get_col_data(data):
    """
    Extract taxonomic and associated information from Catalogue of Life API-result
    :param data: dictionary structure returned from API
    :return: input_name, id, rank, scient_name, status, bib_ref, url
    """
    input_name = data["name"]
    status = data["results"][0]["name_status"]
    if status == 'common name':
        rank = data["results"][0]["accepted_name"]["rank"]
        url = data["results"][0]["accepted_name"]["url"]
        scient_name = data["results"][0]["accepted_name"]["name"]
        col_id = data["results"][0]["accepted_name"]["id"]
        bib_ref = get_bibref_information(data)

    elif status == 'synonym':
        rank = data["results"][0]["rank"]
        url = data["results"][0]["accepted_name"]["url"]
        scient_name = data["results"][0]["accepted_name"]["name"]
        col_id = data["results"][0]["accepted_name"]["id"]
        bib_ref = get_bibref_information(data)

    else:
        col_id = data["results"][0]["id"]
        rank = data["results"][0]["rank"]
        scient_name = data["results"][0]["name"]
        url = data["results"][0]["url"]
        bib_ref = get_bibref_information(data)

    return input_name, col_id, rank, scient_name, status, bib_ref, url


def read_tagged_file(file):
    list_tagged = []
    for line in file:
        tagged_tokens = line.rstrip("\n").split(" ")
        for tagged_token in tagged_tokens:
            try:
                token, tag = tagged_token.split("__")
            except ValueError:
                print("VALUE ERROR no splitting at __ possible in line {}".format(line), file=sys.stderr, flush=True)

            list_tagged.append((token, tag))
        list_tagged.append(("EOS", "EOS"))

    return list_tagged

def _store_empty():
    """
    Store empty strings for un-linkable entity candidate
    :return: empty strings
    """
    return "", "", "", "", "", ""

def send_api_request(BASE_URL, my_atts, no_linked_entities, lookup_table):
    """
    Query API (Catalogue of Life) and store relevant information.
    Unless specified otherwise, name lookups are used for higher entity linking coverage.

    :param BASE_URL: string (query URL)
    :param atts: dictionary (for query attributes)
    :param no_linked_entities: total number of linked entities
    :param lookup_table: dictionary containing vernacular -> scientific name mappings
    :param use_lookup: boolean, if true vernacular -> scientific name lookups are performed
    :return: input_name, id, rank, scient_name, status, bib_ref, url, no_linked_entities
    """
    resp = requests.get(BASE_URL, params=my_atts)
    data = resp.json()

    if data["total_number_of_results"] == 0:
        input_name = data["name"]

        if lookup_table.get(input_name):
            lookup_query_name = lookup_table[input_name][0]
            my_atts['name'] = lookup_query_name
            resp = requests.get(BASE_URL, params=my_atts)
            data = resp.json()
            if data["total_number_of_results"] == 0:
                input_name = data["name"]
                id, rank, scient_name, status, bib_ref, url = _store_empty()
            else:
                input_name, id, rank, scient_name, status, bib_ref, url = get_col_data(data)
                no_linked_entities += 1

        else:
            id, rank, scient_name, status, bib_ref, url = _store_empty()

    else:
        input_name, id, rank, scient_name, status, bib_ref, url = get_col_data(data)
        no_linked_entities += 1

    return input_name, id, rank, scient_name, status, bib_ref, url, no_linked_entities


def process_file(tagged_file):
    """
    Store indices of entity candidates in dictionary and store file information
    :param tagged_file: file-like obj with tagged sentences
    :return: no_total_sentences, no_total_entities, index_dict, query_atts, name_occurrence_dict
    """
    query_atts = {}
    query_atts['format'] = 'json'

    with open(tagged_file, 'r') as tagged:
        list_tagged = read_tagged_file(tagged)
        index_dict = defaultdict(dict)
        name_occurrence_dict = defaultdict()
        sentence_counter = 1
        index_counter = -1
        no_total_sentences = 0
        no_total_entities = 0
        for index, (token, iob_tag) in enumerate(list_tagged):
            index_counter += 1

            if iob_tag == "EOS":
                no_total_sentences += 1
                sentence_counter += 1
                index_counter = -1

            if iob_tag == "O":
                continue
            else:
                if iob_tag.startswith('B-'):
                    # unigram case or case with two separate consecutive tags: B-en_species B-en_fam
                    no_total_entities += 1
                    checkindex = index + 1
                    if list_tagged[checkindex][1] == 'O' or list_tagged[checkindex][1].startswith("B-"):

                        query_atts['name'] = token
                        name_occurrence_dict[token] = token
                        uni_index = index_counter

                        try:
                            index_dict[token][sentence_counter] += [uni_index]
                        except KeyError:
                            index_dict[token][sentence_counter] = []
                            index_dict[token][sentence_counter] += [uni_index]

                    else:
                        # bigram case: (only 2 tokens)
                        if list_tagged[checkindex][1].startswith('I-') and list_tagged[checkindex + 1][1] == 'O':
                            bigram_name = token + " " + list_tagged[checkindex][0]
                            query_atts['name'] = bigram_name
                            name_occurrence_dict[bigram_name] = bigram_name
                            start_index, end_index = index_counter, index_counter + 1
                            try:
                                index_dict[bigram_name][sentence_counter] += [(start_index, end_index)]
                            except KeyError:
                                index_dict[bigram_name][sentence_counter] = []
                                index_dict[bigram_name][sentence_counter] += [(start_index, end_index)]

                        else:
                            # ngram case with more than 2 tokens
                            bigram_name = token + " " + list_tagged[checkindex][0]  # for API query
                            query_atts['name'] = bigram_name

                            temp_index_counter = index_counter
                            temp_start_index = index_counter

                            ngram_name = []
                            ngram_name.append(bigram_name)

                            while list_tagged[checkindex + 1][1] != 'O':
                                checkindex += 1
                                ngram_name.append(list_tagged[checkindex][0])
                                joined_ngram_name = " ".join(ngram_name)
                                start_index, end_index = temp_start_index, index_counter + 2
                                index_counter += 1

                            try:
                                index_dict[bigram_name][sentence_counter] += [(start_index, end_index)]
                            except KeyError:
                                index_dict[bigram_name][sentence_counter] = []
                                index_dict[bigram_name][sentence_counter] += [(start_index, end_index)]

                            index_counter = temp_index_counter
                            name_occurrence_dict[bigram_name] = joined_ngram_name

                elif iob_tag.startswith('I-'):
                    continue

    return no_total_sentences, no_total_entities, index_dict, query_atts, name_occurrence_dict


def store_reference_db(language):
    """
    Store vernacular scientific name table in a dictionary
    :param language: str language of lookup table
    :return:
    """
    lookup_table = defaultdict(list)
    with open("./reference_db/{}_lat_lookup.tsv".format(language), 'r') as reference_db:
        for line in reference_db:
            line = line.rstrip("\n").lower()
            de, lat = line.split("\t")
            lookup_table[de].append(lat)

    return lookup_table


def create_json(index_dict, query_atts, name_occurrence_dict, lookup_table):
    """
    Create json-object from botanical and positional information about all entity candidates.
    :param index_dict: dictionary containing positional information for each entity candidate
    :param atts: query attributes
    :param name_occurrence_dict: dictionary
    :param lookup_table: dictionary containing vernacular -> scientific name mappings
    :return: json_data (dict), no_linked_entities (int)
    """
    BASE_URL = "http://webservice.catalogueoflife.org/col/webservice?"
    json_data = {}
    json_data['plant_names'] = []
    no_linked_entities = 0

    for query_name, indices in index_dict.items():
        query_atts['name'] = query_name
        inds = {}
        inds["sentence_ID"] = []
        for sent_index, span_index in indices.items():
            if isinstance(span_index[0], tuple):
                name_type = "ngram"
            else:
                name_type = "unigram"

            inds["sentence_ID"].append({
                "sent_ID_{}".format(sent_index): span_index
            })
#BASE_URL, my_atts, no_linked_entities, lookup_table
        input_name, id, rank, scient_name, status, bib_ref, url, no_linked_entities = send_api_request(BASE_URL,
                                                                                                       query_atts,
                                                                                                       no_linked_entities,
                                                                                                       lookup_table)
        json_data['plant_names'].append({
            'entity_candidate': name_occurrence_dict[query_name],
            'api_query_name': query_name,
            'ngram_type': name_type,
            'sentences_indices': inds,
            'id_CoL': id,
            'taxon_rank': rank,
            'associated_scientific_name': scient_name,
            'CoL_status': status,
            'biblio_reference': bib_ref,
            'url_to_CoL_entry': url
        })
    return json_data, no_linked_entities


def main():
    tagged_file_default = "./output.txt"
    json_output_default = "./json_data_outfile.json"

    parser = argparse.ArgumentParser(description='Link found plant names to DB-entries in Catalogue of Life.')

    parser.add_argument(
        '-i', '--input_file',
        type=str,
        default=tagged_file_default,
        help='pass tagged file (The__O wallflower__B-en_species)')

    parser.add_argument(
        '-o', '--json_output',
        type=str,
        default=json_output_default,
        help='pass tagged file (The__O wallflower__B-en_species)')

    parser.add_argument(
        '-l', '--language',
        type=str,
        default=json_output_default,
        help='pass tagged file (The__O wallflower__B-en_species)')

    args = parser.parse_args()
    tagged_file = args.input_file
    json_output = args.json_output
    language = args.language

    lookup_table = store_reference_db(language)

    time1 = time.time()
    no_total_sentences, no_total_entities, index_dict, query_atts, name_occurrence_dict = process_file(tagged_file)
    json_data, no_linked_entities = create_json(index_dict, query_atts, name_occurrence_dict, lookup_table)
    time2 = time.time()
    elapsed = time2 - time1

    with open(json_output, 'w', encoding='utf-8') as outfile:
        json.dump(json_data, outfile, ensure_ascii=False)

    print(15 * "-" + "Entity Linking Performance Evaluation" + 15 * "-" + "\n")
    print(
        "\t-->No. sentences: {}\n\t-->Time for linking: {}\n\t-->Total tagged entities: {}\n\t-->Total linked entities: {}\n"
            .format(no_total_sentences, elapsed, no_total_entities, no_linked_entities),
        file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()