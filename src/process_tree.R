#!/usr/bin/env Rscript

# 接受命令行参数
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) {
  stop("Usage: Rscript process_tree.R <trait>")
}
trait <- args[1]

# 载入包
library(treeio)
library(dplyr)
library(plyr)

# 读取插入 node number 之后的 nexus 树文件
tree <- read.beast("Test_ins.tree")

# 提取数据中的 node name, node height, node length, state
x <- as_tibble(tree)

# 动态构造列名
trait_col <- trait  # 例如 "type"
prob_col <- paste0(trait, ".prob")  # 例如 "type.prob"

# 检查列是否存在
if (!(trait_col %in% colnames(x))) {
  stop(paste("Error: Column", trait_col, "does not exist in the tree data."))
}
if (!(prob_col %in% colnames(x))) {
  stop(paste("Error: Column", prob_col, "does not exist in the tree data."))
}

# 动态选择字段（基于 trait 和 trait.prob）
x2 <- select(x, label, height, branch.length, all_of(trait_col), all_of(prob_col))

# 添加时间信息，从名字中提取
# 复制包含 tip name 和 node name 的 label 到新列 isolate
x2$isolate <- x2$label

# 提取 tip name
tiplab <- tree@phylo[["tip.label"]]

# 删除没用的 node name
x2$isolate[which(!x2$isolate %in% tiplab)] <- ""

# 从名字提取时间
x2$isolate <- gsub(".+_", "", x2$isolate)

# 保存到一个 csv 文件
readr::write_csv(x2, "Treedata.csv")

cat("Tree data processed and saved as tree.data.csv\n")