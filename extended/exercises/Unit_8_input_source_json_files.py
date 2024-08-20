"""
# Streaming app

Reads streaming data from a HDFS directory with files in json format
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split, expr
import sys

def parse_args():
    if len(sys.argv) != 2:
        print("Usage: {} <dir>".format(sys.argv[0]))
        sys.exit(1)
    return sys.argv[1]


if __name__ == "__main__":
    input_path = parse_args()

    spark = SparkSession.builder \
        .appName('StreamingFromFile') \
        .config('spark.sql.shuffle.partitions', 3) \
        .config('spark.streaming.stopGracefullyOnShutdown', 'true') \
        .config('spark.sql.streaming.schemaInference', 'true') \
        .getOrCreate()

    # Source
    df = spark.readStream \
        .format('json') \
        .option('path', input_path) \
        .load()

    df.printSchema()

    # Transform

    # Sink
    query = df.writeStream \
        .format('console') \
        .outputMode('update') \
        .start()

    query.awaitTermination()
