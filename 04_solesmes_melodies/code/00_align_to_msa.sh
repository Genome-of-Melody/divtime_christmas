#!/usr/bin/bash

for i in `ls ../data/*`; do
    mafft --add ../data/$i --text --textmatrix ../../00_tree_inference/code/00_textmatrix_complete \
	  --globalpair --maxiterate 10000 \
	  ../../00_tree_inference/data/"$i"_src.aligned.fasta > ../data/"$i"_wsolesmes.fasta
done

