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
cumesset_solesmes <- cumesset_solesmes[(length(cumesset_solesmes)-2):length(cumesset_solesmes)]
cumesset_solesmes <- paste(cumesset_solesmes, collapse="")
cumesset_solesmes <- unname(unlist(strsplit(cumesset_solesmes, split="")))
# judjer1
judjer1_solesmes <- readLines("../data/judjer1_wsolesmes.fasta")
judjer1_solesmes <- judjer1_solesmes[(length(judjer1_solesmes)-1):length(judjer1_solesmes)]
judjer1_solesmes <- paste(judjer1_solesmes, collapse="")
judjer1_solesmes <- unname(unlist(strsplit(judjer1_solesmes, split="")))
# judjer2
judjer2_solesmes <- readLines("../data/judjer2_wsolesmes.fasta")
judjer2_solesmes <- judjer2_solesmes[(length(judjer2_solesmes)-3):length(judjer2_solesmes)]
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

# print out pp_i and logpp_i
consest_solesmes_pp
log(consest_solesmes_pp)
cumesset_solesmes_pp
log(cumesset_solesmes_pp)
judjer1_solesmes_pp
log(judjer1_solesmes_pp)
judjer2_solesmes_pp
log(judjer2_solesmes_pp)
orisic_solesmes_pp
log(orisic_solesmes_pp)

consest_df <- data.frame(maxpd=maxpd[consest_idx], solesmes=consest_solesmes)
cumesset_df <- data.frame(maxpd=maxpd[cumesset_idx], solesmes=cumesset_solesmes)
judjer1_df <- data.frame(maxpd=maxpd[judjer1_idx], solesmes=judjer1_solesmes)
judjer2_df <- data.frame(maxpd=maxpd[judjer2_idx], solesmes=judjer2_solesmes)
orisic_df <- data.frame(maxpd=maxpd[orisic_idx], solesmes=orisic_solesmes)

consest_rm <- which((consest_df$maxpd == "-") & (consest_df$solesmes == "-"))
cumesset_rm <- which((cumesset_df$maxpd == "-") & (cumesset_df$solesmes == "-"))
judjer1_rm <- which((judjer1_df$maxpd == "-") & (judjer1_df$solesmes == "-"))
judjer2_rm <- which((judjer2_df$maxpd == "-") & (judjer2_df$solesmes == "-"))
orisic_rm <- which((orisic_df$maxpd == "-") & (orisic_df$solesmes == "-"))

# removing all-dash positions in both melodies
consest_df <- consest_df[-consest_rm,]
cumesset_df <- cumesset_df[-cumesset_rm,]
judjer1_df <- judjer1_df[-judjer1_rm,]
judjer2_df <- judjer2_df[-judjer2_rm,]
orisic_df <- orisic_df[-orisic_rm,]

# states with pp=0 produce -Inf for sum logpp or 0 for prod pp, which indet the whole melody PP  
#exp(sum(log(consest_solesmes_pp)))
consest_solesmes_pp_na <- consest_solesmes_pp
cumesset_solesmes_pp_na <- cumesset_solesmes_pp
judjer1_solesmes_pp_na <- judjer1_solesmes_pp
judjer2_solesmes_pp_na <- judjer2_solesmes_pp
orisic_solesmes_pp_na <- orisic_solesmes_pp

consest_solesmes_pp_na[which(consest_solesmes_pp_na == 0)] <- NA
cumesset_solesmes_pp_na[which(cumesset_solesmes_pp_na == 0)] <- NA
judjer1_solesmes_pp_na[which(judjer1_solesmes_pp_na == 0)] <- NA
judjer2_solesmes_pp_na[which(judjer2_solesmes_pp_na == 0)] <- NA
orisic_solesmes_pp_na[which(orisic_solesmes_pp_na == 0)] <- NA

# Solesmes pp_melody after removing general dashes and 0-prob values
prod(consest_solesmes_pp_na, na.rm=TRUE)
prod(cumesset_solesmes_pp_na, na.rm=TRUE)
prod(judjer1_solesmes_pp_na, na.rm=TRUE)
prod(judjer2_solesmes_pp_na, na.rm=TRUE)
prod(orisic_solesmes_pp_na, na.rm=TRUE)
sum(log(consest_solesmes_pp_na), na.rm=TRUE)
sum(log(cumesset_solesmes_pp_na), na.rm=TRUE)
sum(log(judjer1_solesmes_pp_na), na.rm=TRUE)
sum(log(judjer2_solesmes_pp_na), na.rm=TRUE)
sum(log(orisic_solesmes_pp_na), na.rm=TRUE)


### maxpd melodies
# print the vector of pp for each position in the consest melody at the root node

# get the max pd values for each position, for each node, rather than the symbol
# there are 14 internal nodes, get the maxpd states for a given node
maxpd_values <- matrix(nrow=nrow(paces[[1]]), ncol=length(msa))
rownames(maxpd_values) <- rownames(paces[[1]])
# fill in the variants with maxpd
for (i in 1:nrow(maxpd_values)) {
    for (j in variants) {
        maxpd_values[i,j] <- max(paces[[j]][i,])
    }
}
# fill in the invariants
for (i in 1:nrow(maxpd_values)) {
    for (j in invariants) {
        maxpd_values[i,j] <- 1.0
    }
}

# calculate pp_melody for the reconstruction at the root node
prod(maxpd_values[consest_idx], na.rm=TRUE)
prod(maxpd_values[cumesset_idx], na.rm=TRUE)
prod(maxpd_values[judjer1_idx], na.rm=TRUE)
prod(maxpd_values[judjer2_idx], na.rm=TRUE)
prod(maxpd_values[orisic_idx], na.rm=TRUE)
sum(log(maxpd_values[consest_idx]), na.rm=TRUE)
sum(log(maxpd_values[cumesset_idx]), na.rm=TRUE)
sum(log(maxpd_values[judjer1_idx]), na.rm=TRUE)
sum(log(maxpd_values[judjer2_idx]), na.rm=TRUE)
sum(log(maxpd_values[orisic_idx]), na.rm=TRUE)



# build a table for the results
pp_melody_solesmes <- c(prod(consest_solesmes_pp_na, na.rm=TRUE),
prod(cumesset_solesmes_pp_na, na.rm=TRUE),
prod(judjer1_solesmes_pp_na, na.rm=TRUE),
prod(judjer2_solesmes_pp_na, na.rm=TRUE),
prod(orisic_solesmes_pp_na, na.rm=TRUE))

logpp_melody_solesmes <- c(sum(log(consest_solesmes_pp_na), na.rm=TRUE),
sum(log(cumesset_solesmes_pp_na), na.rm=TRUE),
sum(log(judjer1_solesmes_pp_na), na.rm=TRUE),
sum(log(judjer2_solesmes_pp_na), na.rm=TRUE),
sum(log(orisic_solesmes_pp_na), na.rm=TRUE))

pp_melody_ancstate <- c(prod(maxpd_values[consest_idx], na.rm=TRUE),
prod(maxpd_values[cumesset_idx], na.rm=TRUE),
prod(maxpd_values[judjer1_idx], na.rm=TRUE),
prod(maxpd_values[judjer2_idx], na.rm=TRUE),
prod(maxpd_values[orisic_idx], na.rm=TRUE))

logpp_melody_ancstate <- c(sum(log(maxpd_values[consest_idx]), na.rm=TRUE),
sum(log(maxpd_values[cumesset_idx]), na.rm=TRUE),
sum(log(maxpd_values[judjer1_idx]), na.rm=TRUE),
sum(log(maxpd_values[judjer2_idx]), na.rm=TRUE),
sum(log(maxpd_values[orisic_idx]), na.rm=TRUE))

probs_table <- data.frame(melody=c("consest", "cumesset", "judjer1", "judjer2", "orisic", "consest", "cumesset", "judjer1", "judjer2", "orisic"),
                          type=c(rep("ancstate", times=5), rep("solesmes", times=5)),
                          prob=c(pp_melody_ancstate, pp_melody_solesmes),
                          logprob=c(logpp_melody_ancstate, logpp_melody_solesmes))

probs_table[order(probs_table$melody),]
