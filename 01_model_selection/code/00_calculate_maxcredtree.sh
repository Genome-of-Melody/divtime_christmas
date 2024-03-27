#!/usr/bin/bash

# combine the tree samples
pxlog -t ../../00*/analysis/*.run*.t -b 500 | pxt2new -o ../data/combined_trees.newick
rm phyx.logfile

treeannotator -file ../data/combined_trees.newick ../data/maxcredtree.tre
