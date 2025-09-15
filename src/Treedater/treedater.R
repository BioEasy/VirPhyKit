require(treedater)
require(ape)
require(ggplot2)

args <- commandArgs(trailingOnly = TRUE)
tree_file <- args[1]
metadata_file <- args[2]
seqlen <- as.numeric(args[3])
output_dir <- args[4]
plot_ltt <- as.logical(args[5])


tre <- read.tree(tree_file)


Times <- read.csv(metadata_file, header = TRUE)
sts <- setNames(Times[,2], Times[,1])

dtr <- dater(tre, sts, seqlen, clock = "uncorrelated")

pdf(file.path(output_dir, "Phylogeny.pdf"), width = 10, height = 8)
plot(dtr, no.mar = TRUE, cex = 0.5)
dev.off()


if (plot_ltt) {
  pb <- parboot(dtr, ncpu = 1)
  g <- plot(pb, ggplot = TRUE)
  ggsave(file.path(output_dir, "LTT.pdf"), plot = g, width = 10, height = 8)
}


cat(capture.output(print(dtr)), sep = "\n")