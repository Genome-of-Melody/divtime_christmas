#!/usr/bin/bash

cd ../analysis

ln -s ../code/01_tree_inference.mb 01_tree_inference.mb
ln -s ../data/concatenated.nexus concatenated.nexus

mpirun -n 12 --oversubscribe mrbayes_volpiano-mpi 01_tree_inference.mb
