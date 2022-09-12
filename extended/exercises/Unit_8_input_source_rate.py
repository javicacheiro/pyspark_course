"""
# Streaming app

Reads streaming data from a rate source
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split, expr

if __name__ == "__main__":

    spark = SparkSession.builder \
        .appName('StreamingFromFile') \
        .config('spark.sql.shuffle.partitions', 3) \
        .config('spark.streaming.stopGracefullyOnShutdown', 'true') \
        .config('spark.sql.streaming.schemaInference', 'true') \
        .getOrCreate()

    # Source
    df = spark.readStream \
        .format('rate') \
        .option('rowsPerSecond', 2) \
        .option('numPartitions', 2) \
        .load()

    df.printSchema()

    # Transform

    # Sink
    query = df.writeStream \
        .format('console') \
        .outputMode('update') \
        .start()

    query.awaitTermination()
