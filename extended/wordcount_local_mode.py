from __future__ import print_function
from pyspark.sql import SparkSession

if __name__ == '__main__':
    spark = SparkSession\
        .builder \
        .appName("WordCount") \
        .master("local[3]") \
        .getOrCreate()
    sc = spark.sparkContext

    lines = sc.textFile('/etc/hosts')
    words = lines.flatMap(lambda line: line.split())
    counts = words.map(lambda word: (word, 1))
    aggregated = counts.reduceByKey(lambda a, b: a + b)
    result = aggregated.map(lambda x_y: (x_y[1], x_y[0]))
    print(result.sortByKey(ascending=False).take(10))

    spark.stop()
