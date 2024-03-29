logliks <- read.delim("../analysis/marginal_logliks.tsv", header=TRUE)

bayes_factors <- exp(logliks$loglik - max(logliks$loglik))
model_posterior <- bayes_factors/sum(bayes_factors)

df <- data.frame(logliks, bayes_factors, model_posterior)

df_sorted <- df[order(-df$model_posterior), ]

pdf("../analysis/model_posterior_probability.pdf", width=20, height=10)
barplot(height=df_sorted$model_posterior, names.arg=df_sorted$tree, ylab="Model posterior probability")
dev.off()
