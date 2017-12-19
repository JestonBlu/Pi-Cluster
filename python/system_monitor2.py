'''
PySpark job to plot CPU temperature
'''

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, TimestampType
from pyspark.sql.window import Window
from pyspark.sql.functions import *

import pandas as pd
import datetime
#import matplotlib.pyplot as plt

spark = SparkSession \
    .builder \
    .appName("PythonPi") \
    .getOrCreate()

userSchema = StructType() \
    .add("date", "timestamp") \
    .add("rpi1", "double") \
    .add("rpi2", "double") \
    .add("rpi3", "double") \
    .add("rpi4", "double")

# temp read for development
dta = spark.read.csv("data/rpi_stats.csv", schema = userSchema)

# Pull the date from 5 days before today
now = datetime.datetime.now()
dt = now + pd.DateOffset(-3)
dt = dt.strftime("%Y-%m-%d")

# Pull the last 5 days
dtaSub = dta.filter(dta.date > dt)

# Aggregate the data over 3 hours
dtaSub_spark = dtaSub.groupBy(window("date", windowDuration="6 hour")).avg()
dtaSub_spark.registerTempTable("subTab")

# Show the last 6 hours of aggregated observations
dtaSub_spark.printSchema()
spark.sql('SELECT * from subTab order by window desc limit 6').show()

# Convert to a pandas dataframe
dta = dtaSub.toPandas()

dta.index = dta['date']

# Calculate hourly mean
dta_hourly = dta.resample("60T").mean()

# Generic plot
plot_hourly = dta_hourly.plot().get_figure()
plot_hourly.savefig("/home/jeston/projects/pi-cluster/output/cpu.png")
