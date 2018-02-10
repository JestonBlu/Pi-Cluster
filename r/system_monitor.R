library(ggplot2)
library(reshape2)
library(scales)
library(gridExtra)

x = read.csv("/home/jeston/projects/pi-cluster/data/rpi_stats.csv")
x = as.data.frame(x)
x = na.omit(x)
x = melt(x, id.vars = "date")

x$rpi = ""
x$rpi = ifelse(substr(x$variable, 1, 4) == "rpi1", "RPI 1", x$rpi)
x$rpi = ifelse(substr(x$variable, 1, 4) == "rpi2", "RPI 2", x$rpi)
x$rpi = ifelse(substr(x$variable, 1, 4) == "rpi3", "RPI 3", x$rpi)
x$rpi = ifelse(substr(x$variable, 1, 4) == "rpi4", "RPI 4", x$rpi)

x$typ = ""
x$typ = ifelse(substr(x$variable, 6, 13) == "cpu_tmp", "CPU Temp", x$typ)
x$typ = ifelse(substr(x$variable, 6, 13) == "cpu_pct", "CPU % Used",  x$typ)
x$typ = ifelse(substr(x$variable, 6, 13) == "mem_fre", "RAM Free", x$typ)
x$typ = ifelse(substr(x$variable, 6, 13) == "mem_pct", "RAM % Used",  x$typ)

x$date = substr(x$date, 1, 19)
x$date = as.POSIXlt(x$date)

x$rpi = factor(x$rpi)
x$typ = factor(x$typ)

g1 = ggplot(subset(x, typ == 'CPU Temp')) +
  geom_line(aes(x = date, y = value, color = rpi)) +
  scale_x_datetime("") +
  scale_y_continuous("") +
  scale_color_discrete("") +
  facet_wrap(~typ, scales = "free") +
  theme(text = element_text(family = "mono"),
    plot.title = element_text(hjust = .5),
    plot.subtitle = element_text(hjust = .5)) +
  ggtitle("Raspber Pi Cluster Stats", "(Last 24 Hours)")

g2 = ggplot(subset(x, typ == 'CPU % Used')) +
  geom_line(aes(x = date, y = value, color = rpi)) +
  scale_x_datetime("") +
  scale_y_continuous("") +
  scale_color_discrete("", guide = FALSE) +
  facet_wrap(~typ, scales = "free") +
  theme(text = element_text(family = "mono"),
      plot.title = element_text(hjust = .5),
      plot.subtitle = element_text(hjust = .5))

g3 = ggplot(subset(x, typ == 'RAM % Used')) +
  geom_line(aes(x = date, y = value, color = rpi)) +
  scale_x_datetime("") +
  scale_y_continuous("") +
  scale_color_discrete("", guide = FALSE) +
  facet_wrap(~typ, scales = "free") +
  theme(text = element_text(family = "mono"),
        plot.title = element_text(hjust = .5),
        plot.subtitle = element_text(hjust = .5))

ggsave("/home/jeston/projects/pi-cluster/output/cpu.png",
  grid.arrange(g1, arrangeGrob(g2, g3, nrow = 1), nrow = 2),
  width = 7, height = 5)
