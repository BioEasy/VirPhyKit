library(tidyr)
library(ggplot2)

args <- commandArgs(trailingOnly = TRUE)
input_file <- args[1]
output_file <- args[2]
selected_directions <- args[3:length(args)]

data <- read.table(input_file, header = TRUE, sep = "\t")
data_long <- pivot_longer(data, -Year, names_to = "Migration", values_to = "Count")
data_filtered <- data_long[data_long$Migration %in% selected_directions, ]
all_migrations <- unique(data_filtered$Migration)
linetype_values <- rep(1, length(all_migrations))
names(linetype_values) <- all_migrations
within_migrations <- grep("within", all_migrations, ignore.case = TRUE, value = TRUE)
if(length(within_migrations) > 0) {
  linetype_values[within_migrations] <- 2 
}

p <- ggplot(data_filtered, aes(x = Year, y = Count, color = Migration, linetype = Migration)) +
  geom_line() +
  scale_linetype_manual(values = linetype_values, guide = guide_legend(override.aes = list(linetype = linetype_values))) +
  labs(y = expression(Log[10] * "(Migration Events)")) +
  theme_minimal() +
  theme(panel.border = element_rect(color = "black", fill = NA))

ggsave(output_file, plot = p, width = 10, height = 6, device = "pdf")