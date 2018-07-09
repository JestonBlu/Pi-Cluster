'''
PySpark job to plot CPU temperature
'''

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, TimestampType
from pyspark.sql.window import Window
from pyspark.sql.functions import *

import pandas as pd
import datetime

spark = SparkSession \
    .builder \
    .appName("System Monitor") \
    .getOrCreate()

userSchema = StructType() \
    .add("date", "timestamp") \
    .add("rpi1_cpu_tmp", "double") \
    .add("rpi1_cpu_pct", "double") \
    .add("rpi1_mem_pct", "double") \
    .add("rpi1_mem_fre", "double") \
    .add("rpi2_cpu_tmp", "double") \
    .add("rpi2_cpu_pct", "double") \
    .add("rpi2_mem_pct", "double") \
    .add("rpi2_mem_fre", "double") \
    .add("rpi3_cpu_tmp", "double") \
    .add("rpi3_cpu_pct", "double") \
    .add("rpi3_mem_pct", "double") \
    .add("rpi3_mem_fre", "double")

# Read file from share drive
dta = spark.read.csv("/home/jeston/nfs/rpi_stats.csv", schema = userSchema)

# desktop development
# dta = spark.read.csv("data/rpi_stats.csv", schema = userSchema)

# Pull the date from 5 days before today
now = datetime.datetime.now()
dt = now + pd.DateOffset(-3)
dt = dt.strftime("%Y-%m-%d")

# Pull the last 5 days
dtaSub = dta.filter(dta.date > dt)

# Aggregate the data over 3 hours
dtaSub = dtaSub.groupBy(window("date", windowDuration="1 day")).avg()

dtaSub.show()
