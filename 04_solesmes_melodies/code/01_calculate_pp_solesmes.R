library(ape)

rm(list=ls())

# load results from ancstate
load("../../03_anc_melody_inference/analysis/tree19/ancstate.Rda")

# load alignments with the Solesmes melodies
# consest
consest_solesmes <- readLines("../data/consest_wsolesmes.fasta")
consest_solesmes <- consest_solesmes[(length(consest_solesmes)-1):length(consest_solesmes)]
consest_solesmes <- paste(consest_solesmes, collapse="")
consest_solesmes <- unname(unlist(strsplit(consest_solesmes, split="")))
# cumesset
cumesset_solesmes <- readLines("../data/cumesset_wsolesmes.fasta")
cumesset_solesmes <- cumesset_solesmes[(length(cumesset_solesmes)-1):length(cumesset_solesmes)]
cumesset_solesmes <- paste(cumesset_solesmes, collapse="")
cumesset_solesmes <- unname(unlist(strsplit(cumesset_solesmes, split="")))
# judjer1
judjer1_solesmes <- readLines("../data/judjer1_wsolesmes.fasta")
judjer1_solesmes <- judjer1_solesmes[(length(judjer1_solesmes)-1):length(judjer1_solesmes)]
judjer1_solesmes <- paste(judjer1_solesmes, collapse="")
judjer1_solesmes <- unname(unlist(strsplit(judjer1_solesmes, split="")))
# judjer2
judjer2_solesmes <- readLines("../data/judjer2_wsolesmes.fasta")
judjer2_solesmes <- judjer2_solesmes[(length(judjer2_solesmes)-1):length(judjer2_solesmes)]
judjer2_solesmes <- paste(judjer2_solesmes, collapse="")
judjer2_solesmes <- unname(unlist(strsplit(judjer2_solesmes, split="")))
# orisic
orisic_solesmes <- readLines("../data/orisic_wsolesmes.fasta")
orisic_solesmes <- orisic_solesmes[(length(orisic_solesmes)-1):length(orisic_solesmes)]
orisic_solesmes <- paste(orisic_solesmes, collapse="")
orisic_solesmes <- unname(unlist(strsplit(orisic_solesmes, split="")))

# fetch pp for a single position on the paces list of ancstates
# symbol: char, the symbol in a melody fopr which we want the PP
# position_in_melody: int, the position in the melody
# idx_melody: int vector with the positions in the grand ace object to be subsetted so that we can refer to the position in the melody of interest
# node: char, the _name_ of the node from the pp table for each position. Root is ntips+1 in ape
# ancstates: list, the output of Bayesian ace from the previous analysis
get_pp_position <- function(symbol, position_in_melody, idx_melody, node, ancstates) {
    ancmelody <- ancstates[idx_melody]
    # if the state is in the table, return its pp, otherwise its pp = 0.0
    if (symbol %in% colnames(ancmelody[[position_in_melody]])) {
        pp <- ancmelody[[position_in_melody]][node, symbol]
    } else {
        return(0.0)
    }
    return(pp)
}
# try the function with the first element in the consest solesmes melody against the posterior distribution of states
get_pp_position(symbol=consest_solesmes[1],
                position_in_melody=1,
                idx_melody=consest_idx,
                node="15",
                ancstates=paces)

# print the vector of pp for each position in the consest melody at the root node
consest_solesmes_pp <- vector(mode="numeric", length=length(consest_solesmes))
for (i in seq_along(consest_solesmes)) {
    consest_solesmes_pp[i] <- get_pp_position(symbol=consest_solesmes[i],
                                              position_in_melody=i,
                                              idx_melody=consest_idx,
                                              node="15",
                                              ancstates=paces)
}

cumesset_solesmes_pp <- vector(mode="numeric", length=length(cumesset_solesmes))
for (i in seq_along(cumesset_solesmes)) {
    cumesset_solesmes_pp[i] <- get_pp_position(symbol=cumesset_solesmes[i],
                                              position_in_melody=i,
                                              idx_melody=cumesset_idx,
                                              node="15",
                                              ancstates=paces)
}

# mafft --add on judjer1 generated an alignment which is longer than the original!
judjer1_solesmes_pp <- vector(mode="numeric", length=length(judjer1_solesmes))
for (i in seq_along(judjer1_solesmes)) {
    judjer1_solesmes_pp[i] <- get_pp_position(symbol=judjer1_solesmes[i],
                                              position_in_melody=i,
                                              idx_melody=judjer1_idx,
                                              node="15",
                                              ancstates=paces)
}

judjer2_solesmes_pp <- vector(mode="numeric", length=length(judjer2_solesmes))
for (i in seq_along(judjer2_solesmes)) {
    judjer2_solesmes_pp[i] <- get_pp_position(symbol=judjer2_solesmes[i],
                                              position_in_melody=i,
                                              idx_melody=judjer2_idx,
                                              node="15",
                                              ancstates=paces)
}

orisic_solesmes_pp <- vector(mode="numeric", length=length(orisic_solesmes))
for (i in seq_along(orisic_solesmes)) {
    orisic_solesmes_pp[i] <- get_pp_position(symbol=orisic_solesmes[i],
                                              position_in_melody=i,
                                              idx_melody=orisic_idx,
                                              node="15",
                                              ancstates=paces)
}




# states with pp=0 produce -Inf for sum logpp or 0 for prod pp, which indet the whole melody PP  
#exp(sum(log(consest_solesmes_pp)))
