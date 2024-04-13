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

```
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
```

## Running the phylogeny/DTE/ASR pipeline

### Bayesian tree inference

Multiple sequence alignment was carried out using the notebook `00_tree_inference/code/00_alignment.ipynb`. We use the fasta-formated sequences from the previous step in order to align using `mafft` with a custom score matrix (`00_textmatrix_complete`). Some reformatting is necessary before the files can be used for Bayesian inference, and these are carried out by `phyx` also in the same Python notebook.

Tree inference is carried out by `mrbayes_volpiano` as triggered by the script `00_tree_inference/code/01_run_tree_inference.sh`, which uses the `mrbayes_volpiano` script `01_tree_inference.mb`. This step uses the concatenated alignment `00_tree_inference/data/concatenated.nexus` and returns the analysis output to `00_tree_inference/analysis`.

## Model selection on alternative rooting points

Bayesian model selection using stepping stones is carried out on the maximum clade credibility tree, which is calculated in `01_model_selection/code/00_calculate_maxcredtree.sh` using `phyx` and `treeannotator`.

Then all the possible rooting positions on the MCC tree are generated by `01_model_selection/code/01_reroot_trees.R` using the packages `ape` and `phytools` in `R`. The script `01_model_selection/code/` takes the tree file generated in this step and concatenates it to a general nexus file with both the concatenated alignment from `00_tree_inference/data` and an intermediate file with the tree block including all 25 possible rooted trees.

The script `01_model_selection/code/03_run_stepping_stones.sh` runs the analysis on the input files in `01_model_selection/data` and the template script `01_model_selection/code/stepping_stones.mb` for each of the 25 possible trees and saves the output in a dedicated directory name with the tree ID.

Collection of marginal lnL data are done grepping the log files and keeping the tree ID directory name and the lnL value with:

```bash
grep -a "Mean: " ../analysis/*/*log
```

These values are then stored manually into the file `01_model_selection/analysis/marginal_logliks.tsv`. This is the input for the script `01_model_selection/code/04_summarise_marginal_loglik.R` which generates a barplot with the model posterior probabilities for each tree and saves it to `01_model_selection/analysis/model_posterior_probability.pdf`

The results suggest that the `tree7` is the best one with a model posterior probability higher than 0.7. This is the input for the subsequent analyses.

## Divergence time estimation

This analysis is carried out by `mrbayes_volpiano` using the script `02_divtime/code/00_run_mcmc_sampling.sh`, which in turn uses the concatenated alingment and trees from `01_model_selection/data/alignment_and_trees.nexus`, and then runs an analysis under the prior and under the posterior using the template script `02_divtime/code/mcmc_sampling.mb`.

The age information used as calibration densities is found in Table S1 below:

Table S1. Calibration densities (CD) used in DTE. Time scale is in both years before the present (YBP, as used by `mrbayes_volpiano`) as well as in anno Domini (AD). Single time values represent fixed values whereas intervals represent Uniform(min,max) calibration densities.

| Node              | CD (YBP)   | CD (AD)    |
|-------------------|------------|------------|
| A VOR Cod 259 I   | 654        | 1370       |
| A Wn 1799         | 724--824   | 1200--1300 |
| CDN Hsmu M2149 L4 | 474        | 1550       |
| CH E 611          | 624--724   | 1300--1400 |
| CZ HKm II A 4     | 554        | 1470       |
| CZ PLm 504 C 004  | 408        | 1616       |
| CZ Pn XV A 10     | 624--674   | 1350--1400 |
| CZ Pu I D 20      | 624--674   | 1350--1400 |
| CZ Pu XVII E 1    | 474--524   | 1500--1550 |
| D KA Aug LX       | 624--924   | 1100--1400 |
| D KNd 1161        | 799--849   | 1175--1225 |
| F Pn lat 12044    | 874--924   | 1100--1150 |
| F Pn lat 15181    | 674--724   | 1300--1350 |
| NL Uu 406         | 624--924   | 1100--1400 |
| Root              | 1124--1324 | 700--900   |

The result for this analysis is stored in `02_divtime/analysis/tree7`.

The summarised tree file `02_divtime/analysis/tree7/posterior/alignment_and_trees.nexus.con.tre` is then read by `figtree` in order to produce the Figure 1. This is carried out incorporating an offset of -408, reversing the time axis, and then plotting the HPD interval for the node ages and colouring branches with median IgrBranch rates. The tree is then plotted in units of years before present.

## Ancestral melody reconstruction

The script `03_anc_melody_inference/code/00_ancmelody_reconstruction.R` will take as input the calibrated tree in `02_divtime/analysis/tree7/posterior/alignment_and_trees.nexus.con.tre` and the alignment in `00_tree_inference/data/concatenated.nexus`. This step is very time-consuming and we used a cluster with 64 threads available for processing the 544 total melody positions for the six melodies analysed. The job was submitted with `03_anc_melody_inference/code/anc_melody_inference.pbs`. The analysis returns the maximum _a posteriori_ melody reconstructions in tsv format for each of the melodies, for each of the nodes by picking the states with highest posterior pobability. It also saves an R binary data object with the results as that step is very slow to re-generate frequently.

## Analysis of the Solesmes reconstructions

We used `mafft` again to align the edited reconstructions of five of the melodies availabler in the Solesmes edited compilation, but keeping the base aligment unchanged. This allowed us to track equivalent positions between the Solesmes melodies and our ancestral melody reconstrctions. This also allowed to calculate melody posterior probabilities for both reconstructions and compare them across the internal nodes. Multiple sequence alignment incorporating the Solesmes melodies in `04_solesmes_melodies/data` was carried out by the script `04_solesmes_melodies/code/00_align_to_msa.sh`.

Then the results in binary format from the ancestral melody reconstruction were loaded again and used to generate a table with melody posterior probability and its log for an arbitrary internal node ID, which is done by `04_solesmes_melodies/code/01_calculate_pp_solesmes.R` which is actually called iteratively over all the internal node IDs by `04_solesmes_melodies/code/01_calculate_pp_foreach_node.sh`. This script will generate tsv tables with the melody probabilities at a given internal node.

## Postprocessing

The Ancestral State Reconstruction results can be postprocessed back into a CantusCorpus-style
CSV with the `postprocess_ancstate_into_csv.py` script. The result can then be loaded e.g. into
ChantLab for analysis.
