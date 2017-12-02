'''
'''

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, TimestampType
from pyspark.sql.window import Window
from pyspark.sql.functions import *

import pandas as pd
import datetime
import matplotlib.pyplot as plt

spark = SparkSession \
    .builder \
    .config("spark.driver.bindAddress", "127.0.0.1") \
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
dt = now + pd.DateOffset(-10)
dt = dt.strftime("%Y-%m-%d")

# Pull the last 5 days
dtaSub = dta.filter(dta.date > dt)

# Aggregate the data over 3 hours
w = dtaSub.groupBy(window("date", windowDuration="3 hour")).avg()

w.show()
