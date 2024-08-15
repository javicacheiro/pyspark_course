"""
# Streaming app

Reads streaming data from a kafka topic
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split, expr
import os

if __name__ == "__main__":

    spark = SparkSession.builder \
        .appName('StreamingFromKafka') \
        .config('spark.sql.shuffle.partitions', 3) \
        .config('spark.streaming.stopGracefullyOnShutdown', 'true') \
        .config('spark.sql.streaming.schemaInference', 'true') \
        .getOrCreate()

    # Source
    df = spark.readStream \
        .format('kafka') \
        .option("kafka.bootstrap.servers", os.environ["BROKER"]) \
        .option("subscribe", os.environ["TOPIC"]) \
        .load()

    df.printSchema()

    # Transform

    # Sink
    query = df.writeStream \
        .format('console') \
        .outputMode('update') \
        .start()

    query.awaitTermination()
