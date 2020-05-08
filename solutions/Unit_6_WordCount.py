from __future__ import print_function
from pyspark.sql import SparkSession

if __name__ == '__main__':
    spark = SparkSession\
        .builder \
        .appName("WordCount") \
        .config('spark.driver.memory', '2g') \
        .config('spark.executor.cores', 1) \
        .config('spark.executor.memory', '2g') \
        .config('spark.executor.memoryOverhead', '1g') \
        .config('spark.dynamicAllocation.enabled', False) \
        .getOrCreate()
    sc = spark.sparkContext

    lines = sc.textFile('datasets/slurmd/slurmd.log.c6601')
    words = lines.flatMap(lambda line: line.split())
    counts = words.map(lambda word: (word, 1))
    aggregated = counts.reduceByKey(lambda a, b: a + b)
    result = aggregated.map(lambda (x, y): (y, x))
    result.sortByKey(ascending=False).take(10)

    spark.stop()
