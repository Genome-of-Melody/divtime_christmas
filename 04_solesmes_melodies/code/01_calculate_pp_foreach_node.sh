#!/usr/bin/bash


for i in {15..27}; do
    Rscript 01_calculate_pp_solesmes.R $i
done
