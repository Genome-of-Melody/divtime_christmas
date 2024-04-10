# divtime_christmas


## Datasets

The `source_data` folder contains the source datasets (Christmas and Solesmes) used in experiments.
They are present as CantusCorpus-style CSV files.

The current version of the Christmas dataset is available as `christmas_dataset_ismir2024.csv`.
Compared to ISMIR 2023, additional cleaning has been applied: differentiae and other cues such
as repetenda were removed,  the Cistercian melodies for the Judea et Jerusalem responsory 
and its verse Constantes estote was transposed a fifth down to be compatible with the rest of the sources.

## Preprocessing

In order to obtain inputs for the bioinformatics pipeline, we need to further preprocess
the melodies. For phylogeny buidling, melodies should contain only notes and neume/syllable/word
separators using the standard volpiano dashes. All barlines and other non-note characters
should be removed. (The preprocessing steps in phylogeny building then takes care of the separators:
in some settings we might prefer to retain them.) This is done by the `clean_christmas.py` script
(use flags `-cbnder` for the full cleaning).

In order to get valid inputs for alignment, we then must create FASTA files 
(with sigla as sequence names) individually for all
the chants. This step is implemented by the `build_src_fasta.py` script.

The list of sigla that are retained (because these sources contain enough
of all the Cantus IDs that we are analysing):

A-VOR Cod. 259/I
A-Wn 1799**
CDN-Hsmu M2149.L4
CH-E 611
CZ-HKm II A 4
CZ-PLm 504 C 004
CZ-Pn XV A 10
CZ-Pu I D 20
CZ-Pu XVII E 1
D-KA Aug. LX
D-KNd 1161
F-Pn lat. 12044
F-Pn lat. 15181
NL-Uu 406



## Running the phylogeny/DTE/ASR pipeline


...


## Postprocessing

The Ancestral State Reconstruction results can be postprocessed back into a CantusCorpus-style
CSV with the `postprocess_ancstate_into_csv.py` script. The result can then be loaded e.g. into
ChantLab for analysis.