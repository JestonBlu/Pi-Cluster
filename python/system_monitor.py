'''
'''

from pyspark.sql import SparkSession
import pandas as import pd

spark = SparkSession \
    .builder \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .appName("PythonPi") \
    .getOrCreate()
