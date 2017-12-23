import pandas as pd
import datetime
import matplotlib.pyplot as plt

# Read in csv
dta_hourly = pd.read_csv("/home/jeston/projects/pi-cluster/data/rpi_avg.csv")
dta_hourly.index = dta_hourly['date']

# Calculate hourly mean
dta_hourly = dta.resample("60T").mean()
dta_hourly.head()

# # Generic plot
plot_hourly = dta_hourly.plot().get_figure()
plot_hourly.savefig("/home/jeston/Projects/pi-cluster/output/cpu.png")
