#!/usr/bin/bash

cd ../analysis

for i in {11,19}; do
    mkdir tree$i
    cd tree$i
    # sample from prior
    mkdir prior
    cd prior
    cp ../../../code/mcmc_sampling.mb ./
    sed -e "s/TREEN/tree$i/g" -i mcmc_sampling.mb
    sed -e "s/TOGGLEDATA/no/g" -i mcmc_sampling.mb
    ln -s ../../../../01_model_selection/data/alignment_and_trees.nexus alignment_and_trees.nexus
    mpirun -n 20 --oversubscribe mrbayes_volpiano-mpi mcmc_sampling.mb
    cd ..
    # sample from posterior
    mkdir posterior
    cd posterior
    cp ../../../code/mcmc_sampling.mb ./
    sed -e "s/TREEN/tree$i/g" -i mcmc_sampling.mb
    sed -e "s/TOGGLEDATA/yes/g" -i mcmc_sampling.mb
    ln -s ../../../../01_model_selection/data/alignment_and_trees.nexus alignment_and_trees.nexus
    mpirun -n 20 --oversubscribe mrbayes_volpiano-mpi mcmc_sampling.mb
    cd ../..
done

