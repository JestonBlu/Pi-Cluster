from pyspark.sql import SparkSession, SQLContext

spark = (SparkSession.builder
    .master("local")
    .appName("Word Count")
    .config("spark.some.config.option", "some-value")
    .getOrCreate()
    )

df = spark.read.csv("/home/jeston/Projects/datasets/mcdonalds.csv")

df = df.toDF()
df.printSchema()
f
