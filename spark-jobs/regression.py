'''
Spark job for regression analysis
'''

from pyspark.ml.classification import LogisticRegression
from pyspark.mllib.regression import LabeledPoint
from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .appName("PythonPi") \
    .getOrCreate()

dta = spark.read.csv("data/HOF_tr.csv", header = True, inferSchema = True)

lr = LogisticRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8)
model = lr.fit(dta)
