'''
PySpark job to plot CPU temperature
'''

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, TimestampType
from pyspark.sql.window import Window
from pyspark.sql.functions import *

import pandas as pd
import datetime
import matplotlib.pyplot as plt

#.config("spark.driver.bindAddress", "127.0.0.1") \
spark = SparkSession \
    .builder \
    .appName("System Monitor") \
    .getOrCreate()

userSchema = StructType() \
    .add("date", "timestamp") \
    .add("rpi1", "double") \
    .add("rpi2", "double") \
    .add("rpi3", "double") \
    .add("rpi4", "double")

# Read file from share drive
dta = spark.read.csv("/home/jeston/nfs/rpi_stats.csv", schema = userSchema)
# desktop development
#dta = spark.read.csv("data/rpi_stats.csv", schema = userSchema)

# Pull the date from 5 days before today
now = datetime.datetime.now()
dt = now + pd.DateOffset(-3)
dt = dt.strftime("%Y-%m-%d")

# Pull the last 5 days
dtaSub = dta.filter(dta.date > dt)

# Aggregate the data over 3 hours
#dtaSub_spark = dtaSub.groupBy(window("date", windowDuration="6 hour")).avg()
#dtaSub_spark.printSchema()
#dtaSub_spark.show()

# Convert to a pandas dataframe
dta = dtaSub.collect()
dta = pd.DataFrame(dta, columns=['date','rpi1','rpi2','rpi3','rpi4'])
dta.index = dta['date']

#dta = dtaSub.coalesce(1).toPandas()
#dta.head()
#dta.index = dta['date']

# Calculate hourly mean
dta_hourly = dta.resample("60T").mean()
dta_hourly.head()

# Write to csv
# dta_hourly.to_csv("/home/jeston/projects/pi-cluster/data/rpi_avg.csv")
#
# # Read in csv
# dta_hourly = pd.read_csv("/home/jeston/projects/pi-cluster/data/rpi_avg.csv")
# #dta_hourly.index = dta_hourly['date']
#
# # Generic plot
plot_hourly = dta_hourly.plot().get_figure()
plot_hourly.savefig("/home/jeston/projects/pi-cluster/output/cpu.png")
