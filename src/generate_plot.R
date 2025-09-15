# generate_plot.R
library(tidyr)
library(ggplot2)
library(scales)
library(ggsci)
library(patchwork)


args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 4) {
    stop("Usage: Rscript generate_plot.R <input_file> <output_file> <first_country> <last_country>")
}

input_file <- args[1]
output_file <- args[2]
first_country <- args[3]
last_country <- args[4]


if (!file.exists(input_file)) {
    stop("Input file does not exist: ", input_file)
}


data <- tryCatch(
    read.table(input_file, header = TRUE, sep="\t"),
    error = function(e) stop("Error reading input file: ", e$message)
)


required_cols <- c("Year", "Total")
if (!all(required_cols %in% names(data))) {
    stop("Required columns missing: ", paste(required_cols[!required_cols %in% names(data)], collapse=", "))
}


if (!(first_country %in% names(data)) || !(last_country %in% names(data))) {
    stop("Specified country columns not found in data: ", first_country, " or ", last_country)
}


df <- gather(data, Country, Value, !!sym(first_country):!!sym(last_country))
df <- df[df$Value > 0,]

ylist <- seq(min(df$Year), max(df$Year), 10)
ylen <- length(ylist)
time <- data.frame("Year"=ylist, "Start"=rep(0,ylen), "End"=rep(max(df$Total+2,ylen)))

p1 <- ggplot()+
  geom_rect(data=time, aes(xmin=Year, xmax=Year+5, ymin=Start, ymax=End), fill="lightgreen", alpha=0.2)+
  geom_line(data=df, aes(x=Year, y=Total), color="red")+
  theme_bw()+
  labs(y="Isolates", x="")+
  theme(
    axis.text.x = element_text(angle=25, color="black"),
    axis.text.y = element_text(color="black"),
    panel.grid = element_blank()
  )+
  scale_x_continuous(expand=c(0,0), breaks = pretty_breaks(n=8))+
  scale_y_continuous(expand=c(0,0), limits = c(0,max(df$Total)+2))

p2 <- ggplot(df, aes(x=Year, y=Country))+
  geom_point(aes(color=Country, size=Value))+
  geom_line(aes(color=Country), size=0.5)+
  scale_color_locuszoom()+
  theme_bw()+
  theme(
    panel.border = element_blank(),
    panel.grid = element_blank(),
    axis.ticks=element_blank(),
    axis.text.x=element_blank(),
    legend.title = element_blank(),
    axis.text.y=element_text(size=8, color="black")
  )+
  labs(x="", y="")+
  guides(color=FALSE)+
  scale_size_area()

p3 <- p1 / p2

output_dir <- dirname(output_file)
if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
}


ggsave(output_file, p3, height = 6, width = 7, units = "in")