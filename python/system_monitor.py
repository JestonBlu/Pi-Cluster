'''
'''

from pyspark.sql import SparkSession
import pandas as pd
import matplotlib.pyplot as plt

spark = SparkSession \
    .builder \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .appName("PythonPi") \
    .getOrCreate()

# Read in data
dta = pd.read_csv("data/rpi_stats.csv")

# Make date field the index
dta['date'] = dta['date'].apply(pd.to_datetime)
dta.index = dta['date']
dta = dta[['rpi1', 'rpi2', 'rpi3', 'rpi4']]

# Calculate mean over time
dta.resample('10min').mean()

plt.plot(dta)
