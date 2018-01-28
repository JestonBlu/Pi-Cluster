library(ggplot2)
library(reshape2)
library(SparkR)


sparkR.session()

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
x$typ = ifelse(substr(x$variable, 6, 13) == "cpu_tmp", "CPU TEMP", x$typ)
x$typ = ifelse(substr(x$variable, 6, 13) == "cpu_pct", "CPU PCT",  x$typ)
x$typ = ifelse(substr(x$variable, 6, 13) == "mem_fre", "MEM FREE", x$typ)
x$typ = ifelse(substr(x$variable, 6, 13) == "mem_pct", "MEM PCT",  x$typ)



g1 = ggplot(x) +
  geom_line(aes(x = date, y = value, color = rpi)) +
  scale_color_discrete("") +
  facet_wrap(~typ, scales = "free")

ggsave("output/cpu.png", g1, width = 7, height = 5)
