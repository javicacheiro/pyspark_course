from __future__ import print_function
from pyspark.sql import SparkSession
import sys


def parse_line(line):
    domain_code, page_title, count_views, total_response_size = line.split()
    return (count_views, (domain_code, page_title))


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Please provide the filename to process")
        sys.exit(1)

    filename = sys.argv[1]

    print("Processing: ", filename)

    spark = SparkSession\
        .builder \
        .appName("Wikimedia pageviews processor") \
        .config('spark.driver.memory', '2g') \
        .config('spark.executor.cores', 1) \
        .config('spark.executor.memory', '2g') \
        .config('spark.executor.memoryOverhead', '1g') \
        .config('spark.dynamicAllocation.enabled', False) \
        .getOrCreate()
    sc = spark.sparkContext

    data = sc.textFile(filename)
    counts = data.map(parse_line)
    result = counts.sortByKey(ascending=False)
    result.cache()

    # Save to HDFS
    result.saveAsTextFile('top_' + filename)

    # Print also the top 10 to stdout
    top10 = result.take(10)
    print(top10)

    spark.stop()
