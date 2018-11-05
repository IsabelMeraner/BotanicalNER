# BotanicalNER
Named entity recognition for scientific and vernacular plant names.


Data sets:
Text + Berg corpus:
The Text + Berg corpus is an annotated linguistic corpus consisting of digitized yearbooks of the Swiss Alpine Club (SAC) with mountaineering reports [Volk et al., 2010]. For this work, we used the release no. 151 [Bubenhofer et al., 2015] and applied our previously created gazetteers to select a subset of sentences from the corpus containing at least one scientific or vernacular plant name mention. The size of this subcorpus is equal to 55,997 tokens and represents hereby the second largest data set.

References:
﻿Volk, M., Bubenhofer, N., Althaus, A., Maya, B., Furrer, L., & Ruef, B. (2010). Challenges in Building a Multilingual Alpine Heritage Corpus. Seventh International Conference on Language Resources and Evaluation (LREC). Retrieved from http://dx.doi.org/10.5167/uzh-34264.
﻿Bubenhofer, N., Volk, M., Leuenberger, F., & Wüest, D. (2015). Text+Berg-Korpus (Release 151v012015). Digitale Edition des Jahrbuch des SAC 1864-1923, Echo des Alpes 1872-1924, Die Alpen, Les Alpes, Le Alpi 1925-2014, The Alpine Journal 1969-2008.

Wiki Corpus
We created a corpus from Wikipedia abstracts describing plants of the German vascular plants category.  In this genre, scientific names are usually combinedwith vernacular names within one sentence, which makes this resource very interesting forour project. In this text genre, usually a very systematic and structured writing style isemployed when describing a plant species or other taxonomic levels

PlantBlog Corpus
The third component of our training material is made up by blog articles retrieved from the Internet. Blog authors usually employ a less formal writing styleand tend to use more common plant names since not all potential readers might be botanistsor botanically-minded.

BotLit Corpus
For this data resource we manually selected text passages from historicalbotanical literature that in our eyes contained a high concentration of either scientific orvernacular plant names. Although being less extensive, this data set offers the possibilityto test the performance of our models regarding old writing variants or archaic names. Weincluded text excerpts from Spescha [2009] containing regional descriptions of flora andfauna, originally published in 1806.

Gazetteers:
Due to copyright issues, we will only make available a small subset of our original collected gazetteers for German and Latin plant names.
The plant names listed in these files, were retrieved from Wikipedia using the API.



Annotating plant names:
To annotate the input files, please run the following command.
Please note: When using large gazetteer files or big input files, this may take a while.


$ python3 iobannotate_corpus.py -d ./../data_german -v ./../gazetteers/de -l ./../gazetteers/lat

