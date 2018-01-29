library(ggplot2)
library(reshape2)
library(scales)
library(gridExtra)

#library(SparkR)
#sparkR.session()

x = read.csv("data/rpi_stats.csv")
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

g1 = ggplot(subset(x, typ == 'CPU % Used')) +
  geom_line(aes(x = date, y = value / 100, color = rpi)) +
  scale_x_datetime("") +
  scale_y_continuous("", labels = percent) +
  scale_color_discrete("") +
  facet_wrap(~typ, scales = "free") +
  theme(text = element_text(family = "mono"))

g2 = ggplot(subset(x, typ == 'RAM % Used')) +
geom_line(aes(x = date, y = value / 100, color = rpi)) +
scale_x_datetime("") +
scale_y_continuous("", labels = percent) +
scale_color_discrete("") +
facet_wrap(~typ, scales = "free") +
theme(text = element_text(family = "mono"))

g3 = ggplot(subset(x, typ == 'CPU Temp')) +
geom_line(aes(x = date, y = value / 100, color = rpi)) +
scale_x_datetime("") +
scale_y_continuous("", labels = percent) +
scale_color_discrete("") +
facet_wrap(~typ, scales = "free") +
theme(text = element_text(family = "mono"))

g4 = ggplot(subset(x, typ == 'RAM Free')) +
geom_line(aes(x = date, y = value / 100, color = rpi)) +
scale_x_datetime("") +
scale_y_continuous("", labels = percent) +
scale_color_discrete("") +
facet_wrap(~typ, scales = "free") +
theme(text = element_text(family = "mono"))


g5 = grid.arrange(g1, g2, g3, g4, nrow = 2)

ggsave("output/cpu.png", g1, width = 7, height = 5)




g1
