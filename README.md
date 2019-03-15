# BotanicalNER
Project: Neural Entity Recognition for Scientific and Vernacular Plant Names<br/>
Author: Isabel Meraner<br/>
Institute of Computational Linguistics, University of Zurich (Switzerland), 2019

This repository contains two subfolders “SCRIPTS” and “RESOURCES”.<br/>
In the RESOURCES folder, you can find the following sample output material and data resources:

Please note that the bi-LSTM-CRF architecture used for training was developed by Lample et al. (2016):   
Named Entity Recognition Tool](https://github.com/glample/tagger)   
Lample et al. (2016). Neural Architectures for Named Entity Recognition. URL= [https://arxiv.org/abs/1603.01360](http://arxiv.org/abs/1603.01360)

The adapted files from the bi-LSTM-CRF tagger by Lample et al. (2016) can be found under
'scripts/web_interface/tagger-master/'.
### TRAINING DATA (path = ‘resources/corpora/training corpora/’)
##### Silver standard training corpora (in IOB-format):
• plantblog_corpus_{de|en}.tok.pos.iob.txt<br/>
• wiki_abstractcorpus_{de|en}.tok.pos.iob.txt<br/>
• TextBerg_subcorpus_{de|en}.tok.pos.iob.txt<br/>
• botlit_corpus_{de|en}.tok.pos.iob.txt<br/>

##### Gold standard fold of combined dataset (in IOB-format):
• combined.test.fold1GOLD_{de|en}.txt

##### Fungi testset for in-domain evaluation on held-out entities:
• test_fungi_{de|en}.tok.pos.iobGOLD.txt

### GAZETTEERS (path = ‘resources/gazetteers/’)
Due to copyright restrictions, these gazetteers only comprise a subset based on plant names retrieved from Wikipedia of our original gazetteers.

##### # Vernacular names (German):
• de_fam.txt<br/>
• de_species.txt<br/>

##### # Vernacular names (English):
• en_fam.txt<br/>
• en_species.txt<br/>

##### # Scientific names (Latin):
• lat_fam.txt<br/>
• lat_species.txt<br/>
• lat_genus.txt<br/>
• lat_subfam.txt<br/>
• lat_class.txt<br/>
• lat_order.txt<br/>
• lat_phylum.txt<br/>

##### # Lookup tables for vernacular names:
• {de|en}_lat_referencedatabase.tsv

### bi-LSTM-CRF MODELS (path = ‘resources/models/’)
##### # Best-performing models for German and English (single-dataset evaluation):
• model_combined_chardim29_de<br/>
• model_wiki_dropout0.3_de<br/>
• model_tb_dropout0.7_de<br/>
• model_plantblog_capdim1_de<br/>
• model_botlit_dropout0.3_de<br/>
• model_combined_dropout0.7_en<br/>
• model_wiki_chardim29_en<br/>
• model_tb_capdim1_en<br/>
• model_plantblog_chardim50_en<br/>
• model_s800_dropout0.7_en<br/>

##### # Best-performing models for German and English (cross-dataset evaluation):
• model_wiki_crosscorpus_de_dropout0.3 (cross-corpus setting)<br/>
• model_wiki_crosscorpus_de_capdim1 (fungi test set)<br/>
• model_wiki_crosscorpus_en_preemb_dropout0.5 (cross-corpus setting)<br/>
• model_wiki_crosscorpus_en_capdim1 (fungi test set)<br/>

### TAGGED DATA (path = ‘resources/sample output/’)
##### # Single-dataset model predictions:
• predictions_wiki_{de|en}.output<br/>
• predictions_textberg_{de|en}.output<br/>
• predictions_blogs_{de|en}.output<br/>
• predictions_botlit_{de|en}.output<br/>

##### # Cross-dataset model predictions:
• predictions_model_wiki_test_textberg_{de|en}.output<br/>
• predictions_model_wiki_test_blogs_{de|en}.output<br/>
• predictions_model_wiki_test_botlit_{de|en}.output<br/>

### ENTITY LINKING (path = ‘resources/linked data/’)
##### # Vernacular-scientific lookup-table:
• {de|en}_lat_referencedatabase.tsv

##### # Example JSON-output per data resource:
• json_data_wiki_{de|en}.json<br/>
• json_data_textberg_{de|en}.json<br/>
• json_data_blogs_{de|en}.json<br/>
• json_data_botlit_{de|en}.json<br/>


In the SCRIPTS folder, you can find all Python and bash scripts that have been used during training:

### DATA COLLECTION (path = ‘scripts/data collection/’)
##### # create Text+Berg subset of sentences containing plant names:
`$ python3 get_subset_textberg.py -i ./../TextBerg/SAC/ -o ./subset_textberg_de.txt -g ./../resources/gazetteers/ -l de`

##### # generate Latin plant name abbreviations:
`$ python3 add_latin_abbreviations.py -i ./../resources/gazetteers/lat/lat_species.txt -o ./outfile.txt`

##### # generate German morpholocical variants:
`$ python3 add_german_variants.py -i ./../resources/gazetteers/de/de_fam.txt -o ./outfile.txt`

##### # split German compounds and add name variants:
`$ python3 add_compound_variants.py -i ./../resources/gazetteers/de/de species.txt -o ./outfileGAZ.txt`

##### # create language-specific gazetteers:
`$ python3 create_gazetteers.py -i ./../resources/gazetteers/de/de_species.txt -o outfile.txt`

##### # add name variants to lookup-table:
`$ python3 add_variants_database.py -i ./../resources/gazetteers/lookup_table/de_lat_referencedatabase.tsv -o ./outfile`

##### # create fungi testset from Wikipedia articles:
`$ python3 get_wiki_fungi_testset.py -o ./outfile.txt -c Pilze -l de`

##### # retrieve Wikipedia abstracts and trivial names sections:
`$ python3 retrieve_wiki_sections.py -i ./../resources/gazetteers/lat/lat_species.txt -t ./outfile_trivialsections.txt -a outfile_wikiabstracts.txt -l de`

##### # extract plant names from Catalogue of Life archive:
`$ python3 extracttaxa_cat_of_life -t ./colarchive/taxa/ -v ./colarchive/vernacular/ -l ./latin.out -d ./german.out -e ./english.out -r rest_vernacular.out`

### PREPROCESSING (path = ‘scripts/preprocessing/’)
##### # tokenization:
`$ python3 tokenize_corpus.py -d ./raw_data/ -l de`

##### # part-of-speech tagging:
`$ python3 ./treetagger-python_miotto/pos_tag_corpus.py -d ./../resources/corpora/`

### DICTIONARY-BASED ANNOTATION (path = ‘scripts/annotation/’)
##### # German annotation in IOB-format:
`$ python3 iobannotate_corpus_de.py -d ./../resources/corpora/training_corpora/de/ -v ./../resources/gazetteers/de/ -s ./../resources/gazetteers/lat/ -l de`

##### # English annotation in IOB-format:
`$ python3 iobannotate_corpus_en.py -d ./../resources/corpora/training_corpora/en/ -v ./../resources/gazetteers/en/ -s ./../resources/gazetteers/lat/ -l de:`


### TRAINING (path = ‘scripts/training/’)
##### # K-fold splitting of training data:
`$ python3 kfold_crossvalidation.py -d ./../resources/corpora/training corpora/de/`

##### # Bashscript 5-fold crossvalidation training (examples):
`$ bash bashscript_5foldtraining_preemb_en.sh`
`$ bash bashscript_5foldtraining_preemb_de.sh`

##### # Adapted scripts from Lample et al. (2016):
`$ python train_no_dev.py`
`$ python utils.py`

### EVALUATION (path = ‘scripts/evaluation/’)
##### # Averaged evaluation over 5 folds:
`$ python final_eval_kfold.py -d ./../../evaluation/baseline/model_baseline/ -o ./evaluation_files/`

##### # Evaluation of silver standard:
`$ python evaluate_gold_silver.py -s ./../resources/corpora/gold_standard/de/alldata.test.fold1SILVER de.txt -g ./../resources/corpora/gold_standard/de/combined.test.fold1GOLD de.txt`

##### # Cross-dataset evaluation:
`$ python3 cross_dataset_evaluation.py -s ./silver_standard/plantblog_corpus.test.fold1.txt -t ./tagged_data/model_wiki_test_blog_f1_dropout5.tsv`

##### # File statistics training corpora (size, token, types, averaged length):
`$ python3 file_statistics.py -i ./../resources/corpora/training_corpora/de/`

##### # Transform IOB-format to 1-sentence-per-line (input for tagger.py):
`$ python3 transform_iob_to_sentences.py -i ./../resources/corpora/training_corpora/de/botlit_corpus_de.tok.pos.iob.txt -o botlit_sentences.txt`


### ENTITY LINKING:
##### # Catalogue of Life entity linking and creation of JSON-output:
`$ python3 entity_linker.py -i ./../resources/corpora/training_corpora/de/botlit_corpus de.tok.pos.iob.txt -o ./json_file.json -f IOB -r ./../resources/gazetteers/lookup_table/de_lat_referencedatabase.tsv -l True`

### WEB INTERFACE:
##### # Start web-application:
`$ python3 web application.py`

##### # Domain-adapted tokenization (function):
`tokenize_input(inputText, language)`

##### # Tagging of tokenised input sentence:
`subprocess.call("python3 ./tagger-master/tagger.py -m ./models/{} -i ./output/input_tokenized.txt -o ./output/output_tagged.txt -d ".format(model), shell=True)`

##### # Linking of entity candidates:
`subprocess.call("python3 ./entity_linker.py -i ./output/output_tagged.txt -o ./static/output_linked.json --language {}".format(language), shell=True)`
