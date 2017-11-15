'''
This script is from the spark examples folder, slightly modified. I modified
this script in order to be able to run it interactively in Atom with Hydrogen.
In order for spark to work within Atom I needed to bind the address. I hardcoded
the partitions so that it could be run interactively or by using spark-submit.
'''

from __future__ import print_function
import sys
from random import random
from operator import add

from pyspark.sql import SparkSession

partitions = 100

spark = SparkSession\
    .builder
    .config("spark.driver.bindAddress", "127.0.0.1")
    .appName("PythonPi")
    .getOrCreate()

n = 100000 * partitions


def f(_):
    x = random() * 2 - 1
    y = random() * 2 - 1
    return 1 if x ** 2 + y ** 2 <= 1 else 0

0
count = spark.sparkContext.parallelize(
    range(1, n + 1), partitions).map(f).reduce(add)

print("Pi is roughly %f" % (4.0 * count / n))
