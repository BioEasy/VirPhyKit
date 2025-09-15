rm(list=ls())
suppressWarnings({
  suppressPackageStartupMessages({
    library(ggplot2)
    library(maps)
    library(rnaturalearth)
    library(sf)
    has_ggsci <- requireNamespace("ggsci", quietly = TRUE)
    if (has_ggsci) {
      library(ggsci)
    }
  })
})

args <- commandArgs(trailingOnly = TRUE)
input_file <- args[1]
output_file <- args[2]

mydata <- read.table(input_file, header=TRUE, sep="\t", encoding="utf-8")
mydata$region <- as.factor(mydata$region)

if (!all(c("Longitude", "Latitude", "region") %in% colnames(mydata))) {
  stop("Input file must contain 'Longitude', 'Latitude', and 'region' columns")
}

world <- ne_countries(scale = "medium", returnclass = "sf")

map_title <- "World Map"
aspect_ratio <- 0.5  
buffer_percent <- 0.02  

world_map_data <- st_as_sf(world)
world_map_data <- st_cast(world_map_data, "MULTIPOLYGON")

bbox <- c(xmin = -180, ymin = -90, xmax = 180, ymax = 90)

x_range <- bbox["xmax"] - bbox["xmin"]
y_range <- bbox["ymax"] - bbox["ymin"]


x_buffer <- x_range * buffer_percent
y_buffer <- y_range * buffer_percent


plot_bbox <- c(
  xmin = bbox["xmin"] - x_buffer,
  ymin = bbox["ymin"] - y_buffer,
  xmax = bbox["xmax"] + x_buffer,
  ymax = bbox["ymax"] + y_buffer
)


x_interval <- 30
y_interval <- 30


x_breaks <- seq(-180, 180, by = x_interval)
y_breaks <- seq(-90, 90, by = y_interval)


width <- 12
height <- width * aspect_ratio
pdf(output_file, width=width, height=height)


p <- ggplot() +
  geom_sf(data = world_map_data, aes(geometry = geometry),
          colour = "darkgrey", fill = "lightgrey", size = 0.2) +
  geom_point(data = mydata,
             aes(x = Longitude, y = Latitude, color = region),
             size = 3, alpha = 0.7)


if (has_ggsci) {
  p <- p + ggsci::scale_color_d3() 
}


p <- p + coord_sf(xlim = c(plot_bbox["xmin"], plot_bbox["xmax"]),
           ylim = c(plot_bbox["ymin"], plot_bbox["ymax"]),
           expand = FALSE, crs = st_crs(4326)) +
  scale_x_continuous(breaks = x_breaks) +
  scale_y_continuous(breaks = y_breaks) +
  labs(x = "Longitude", y = "Latitude", title = map_title, color = "Region") +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 16, face = "bold", hjust = 0.5),
    plot.margin = margin(10, 10, 10, 10),
    panel.grid.major = element_line(color = "grey90", size = 0.2),
    panel.grid.minor = element_blank(),
    axis.title = element_text(size = 12),
    axis.text = element_text(size = 10),
    legend.position = "bottom",
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 10)
  )

print(p)
dev.off()