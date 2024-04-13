# divtime_christmas

In general, each sequential step in this process should be run as ordered (e.g., `000_*`, then `00_*`, then `01_*`, up to `04_*`). Each directory contains usually three subdirectories: `code`, `data`, and `analysis`. Procedures are coded in the `code` directory, using input from the `data` directory, and placing intermediate files also in `data`. The final analysis is then using elements of data as input and returning results in `analysis`. Sometimes, output elements from a given analysis are the input for a subsequent analysis, and the code uses either symbolic links or copy of files from one analysis into the other.

## Datasets

The `000_dataset_cleaning/source_data` folder contains the source datasets (Christmas and Solesmes) used in experiments.
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
in some settings we might prefer to retain them.) This is done by the `000_dataset_cleaning/code/clean_christmas.py` script
(use flags `-cbnder` for the full cleaning).

In order to get valid inputs for alignment, we then must create FASTA files 
(with sigla as sequence names) individually for all
the chants. This step is implemented by the `000_dataset_cleaning/code/build_src_fasta.py` script.

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

### Bayesian tree inference

Multiple sequence alignment was carried out using the notebook `00_tree_inference/code/00_alignment.ipynb`. We use the fasta-formated sequences from the previous step in order to align using `mafft` with a custom score matrix (`00_textmatrix_complete`). Some reformatting is necessary before the files can be used for Bayesian inference, and these are carried out by `phyx` also in the same Python notebook.

Tree inference is carried out by `mrbayes_volpiano` as triggered by the script `00_tree_inference/code/01_run_tree_inference.sh`, which uses the `mrbayes_volpiano` script `01_tree_inference.mb`. This step uses the concatenated alignment `00_tree_inference/data/concatenated.nexus` and returns the analysis output to `00_tree_inference/analysis`.

## Model selection on alternative rooting points



## Postprocessing

The Ancestral State Reconstruction results can be postprocessed back into a CantusCorpus-style
CSV with the `postprocess_ancstate_into_csv.py` script. The result can then be loaded e.g. into
ChantLab for analysis.
