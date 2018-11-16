# BotanicalNER
Named entity recognition for scientific and vernacular plant names.


### Data sets:
#### Text + Berg corpus:
The Text + Berg corpus is an annotated linguistic corpus consisting of digitized yearbooks of the Swiss Alpine Club (SAC) with mountaineering reports [Volk et al., 2010]. This repository contains a subset extracted from release no. 151 [Bubenhofer et al., 2015] with a high concentration of botanical entities.

#### Wiki Corpus
This corpus contains Wikipedia abstracts describing plants of the German vascular plants category.  Wikipedia abstracts usually combine scientific names with vernacular names within one sentence, which makes this resource very interesting.

#### PlantBlog Corpus
This data resource consists of blog articles related to plant descriptions, herbal medicine or similar topics retrieved from the Internet held in a more casual writing style.

#### BotLit Corpus
This resource comprises manually selected text passages from historical botanical literature containing a high concentration of either scientific or vernacular plant names. We included text excerpts from Placidus Spescha [2009] containing regional descriptions of Swiss flora and fauna, originally published in 1806.

References:   
Spescha, P. (2009). Beschreibung der Val Tujetsch (1806). Zürich, Switzerland: Chronos Verlag. Retrieved from https://doi.org/10.5281/zenodo.1311777.

#### Gazetteers:
Due to copyright issues, we will only make available a small subset of our original collected gazetteers for German and Latin plant names. The plant names listed in these files, were retrieved from Wikipedia using the API. The names are divided into two separate lists per language to ensure that the correct entity label is assigned during the annotation process.

----

### Annotating plant names:
To annotate the input files, please run the following command.
Please note: When using large gazetteer files or big input files, this may take a while.


`$ python3 iobannotate_corpus.py -d ./../data_german -v ./../gazetteers/de -l ./../gazetteers/lat`

You can pass in one or multiple input folders for annotation by specifying the directory (-d).   
Files in the input directory need to be preprocessed: 1 token, lemma, part-of-speech-tag per line separated by tabs (1 newline to mark sentence boundaries)
If you are in possession of large gazetteers, you can pass them using the parameters -v for the vernacular list and -l for the scientific names.


References:  
Volk, M., Bubenhofer, N., Althaus, A., Maya, B., Furrer, L., & Ruef, B. (2010). Challenges in Building a Multilingual Alpine Heritage Corpus. Seventh International Conference on Language Resources and Evaluation (LREC). Retrieved from http://dx.doi.org/10.5167/uzh-34264.  
Bubenhofer, N., Volk, M., Leuenberger, F., & Wüest, D. (2015). Text+Berg-Korpus (Release 151v012015). Digitale Edition des Jahrbuch des SAC 1864-1923, Echo des Alpes 1872-1924, Die Alpen, Les Alpes, Le Alpi 1925-2014, The Alpine Journal 1969-2008.    
Wikipedia (2018), Liste der Gefäßpflanzen Deutschlands. Retrieved from:https://de.wikipedia.org/w/index.php?title=Liste_der_Gef%C3%A4%C3%9Fpflanzen_Deutschlands&oldid=133647257
