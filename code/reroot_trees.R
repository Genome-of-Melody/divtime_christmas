library(ape)
library(phytools)

rm(list = ls())

# read the maximum credibility tree
tree <- read.nexus(file="../data/concatenated.nexus.maxcredtree.tre")
# add an arbitrary branch length to the zero-length one for better visualisation
tree$edge.length[1] <- min(tree$edge.length[-1])
### do not unroot the tree, the rerooting works best with rooted ones, even when the original tree was unrooted
#tree <- unroot(tree)
# this is an arbitrary tree for testing purposes
#tree <- ape::read.tree(text="((((A:1,B:1):1,C:1):1,D:1):1,E:1);")

# clean tree file before writing again as it is appended and not rewritten later
if (file.exists("rooted_trees.tre")) {
    file.remove("rooted_trees.tre")
}

# get root properties
root_children <- tree$edge[which(!(tree$edge[, 1] %in% tree$edge[, 2])), 2]
root_node <- tree$edge[which(!(tree$edge[, 1] %in% tree$edge[, 2])), 1][1]

# use a safe value for splitting the edge to be used for rooting
position <- min(tree$edge.length)/2

# reroot if unrooted
if (length(root_children) > 2) {
    # first reroot at the first taxon any place and reroot as usual
    cat("Rerooting\n")
    tree <- root(tree, 1, resolve.root=TRUE)
}

# write the first tree to file
tree_i <- tree
tree_i$edge.length <- NULL
write.tree(tree_i, file="rooted_trees.tre", append=TRUE)

# reroot on each possible branch
for (i in 1:nrow(tree$edge)) {
    # skip if the branch involves children to root and the root itself
    if ((tree$edge[i, 2] %in% root_children) | (tree$edge[i,2] == root_node)) {
        cat("Skipping node ", tree$edge[i,2], "\n\n")
        next
    } else {
        # code for the rooted case
        tree_i <- phytools::reroot(tree, tree$edge[i,2], position=position)
        # remove branch lengths to make sure there is nothing wrong in MrBayes
        tree_i$edge.length <- NULL
        cat("Rooting below ", tree$edge[i,2], "\n\n")
        cat(write.tree(tree_i), "\n\n")
        write.tree(tree_i, file="rooted_trees.tre", append=TRUE)
    }
}
