library(ape)
library(phytools)
library(doParallel)
library(foreach)

args <- commandArgs(TRUE)
args <- "tree11"
tr_path <- paste("../../02_divtime/analysis/", args[1], "/posterior/alignment_and_trees.nexus.con.tre", sep="")
tr <- read.nexus(tr_path)

data <- read.nexus.data("../../02_divtime/data/concatenated.nexus")

### doing posterior sampling for a sequence of states
### using stochastic mapping
msa <- as.data.frame(t(as.data.frame(data)))

paces <- list()
length(paces) <- ncol(msa)

#this block below breaks if the position has invariants
# get first the positions of invariants, and assign the value for the 
# invariant positions
invariants <- which(sapply(X=msa, FUN=function(x)length(table(x)))==1)
variants <- which(sapply(X=msa, FUN=function(x)length(table(x)))!=1)
# populate paces with the invariant values
for (j in invariants) {
    paces[j] <- msa[1, j]
}

# prepare parallelisation
doParallel::registerDoParallel(20)
print(getDoParWorkers())

#parallel version of the commented block below
foreach(i=variants, .errorhandling="pass") %dopar% {
    vec <- as.vector(msa[[i]])
    names(vec) <- names(data)
    cat("Starting ace in variant position ", i, "\n", sep="")
    # save memory by just saving the $ace attr of the summary
    # first time in 12 years that I have a genuine reason to use the <<- operator 
    # and that I really know what it's doing
    paces[[i]] <<- summary(make.simmap(tr, vec, model="ER", nsim=1000))$ace
}
stopImplicitCluster()

cat("It took ", tic-toc, " to completion\n", sep="")

## then calculate the posterior ace for the variant sites    
#for (i in variants) {
#    vec <- as.vector(msa[[i]])
#    names(vec) <- names(data)
#    cat("Starting ace in variant position", i, "\n", sep="")
#    # save memory by just saving the $ace attr of the summary
#    paces[[i]] <- summary(make.simmap(tr, vec, model="ER", nsim=1000))$ace
#}

# there are 14 internal nodes, get the maxpd states for a given node
maxpd <- matrix(nrow=nrow(paces[[1]]), ncol=length(msa))
rownames(maxpd) <- rownames(paces[[1]])
# fill in the variants with maxpd
for (i in 1:nrow(maxpd)) {
    for (j in variants) {
        maxpd[i,j] <- paste(names(which(paces[[j]][i,] == max(paces[[j]][i,]))), collapse="/")
    }
}
# fill in the invariants
for (i in 1:nrow(maxpd)) {
    for (j in invariants) {
        maxpd[i,j] <- msa[1,j]
    }
}

### these posterior aces are for the whole concatenated dataset
### the partition positions for the individual melodies are
#AA, ../data/bethnon_src.aligned.fasta.prenexus.nexus = 1-137
#AA, ../data/consest_src.aligned.fasta.prenexus.nexus = 138-241
#AA, ../data/cumesset_src.aligned.fasta.prenexus.nexus = 242-384
#AA, ../data/judjer1_src.aligned.fasta.prenexus.nexus = 385-445
#AA, ../data/judjer2_src.aligned.fasta.prenexus.nexus = 446-641
#AA, ../data/orisic_src.aligned.fasta.prenexus.nexus = 642-720

bethnon_idx <- 1:137
consest_idx <- 138:241
cumesset_idx <- 242:384
judjer1_idx <- 385:445
judjer2_idx <- 446:641
orisic_idx <- 642:720

bethnon_maxpd <- maxpd[, bethnon_idx]
consest_maxpd <- maxpd[, consest_idx]
cumesset_maxpd <- maxpd[, cumesset_idx]
judjer1_maxpd <- maxpd[, judjer1_idx]
judjer2_maxpd <- maxpd[, judjer2_idx]
orisic_maxpd <- maxpd[, orisic_idx]

# save the maxpd estimates to a tab-delimited file
write.table(x=bethnon_maxpd, file=paste("../analysis/", args[1], "/bethnon_maxpd.tsv", sep=""), sep="\t", row.names=TRUE, col.names=FALSE)
write.table(x=consest_maxpd, file=paste("../analysis/", args[1], "/consest_maxpd.tsv", sep=""), sep="\t", row.names=TRUE, col.names=FALSE)
write.table(x=cumesset_maxpd, file=paste("../analysis/", args[1], "/cumesset_maxpd.tsv", sep=""), sep="\t", row.names=TRUE, col.names=FALSE)
write.table(x=judjer1_maxpd, file=paste("../analysis/", args[1], "/judjer1_maxpd.tsv", sep=""), sep="\t", row.names=TRUE, col.names=FALSE)
write.table(x=judjer2_maxpd, file=paste("../analysis/", args[1], "/judjer2_maxpd.tsv", sep=""), sep="\t", row.names=TRUE, col.names=FALSE)
write.table(x=orisic_maxpd, file=paste("../analysis/", args[1], "/orisic_maxpd.tsv", sep=""), sep="\t", row.names=TRUE, col.names=FALSE)

save(list=ls(), file=paste("../analysis/",args[1],"/ancstate.Rda", sep=""))
