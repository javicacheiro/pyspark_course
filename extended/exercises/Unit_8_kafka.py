"""
# Streaming app

Reads streaming data from a kafka topic
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split, expr

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
        .option("kafka.bootstrap.servers", "10.38.28.103:9092") \
        .option("subscribe", "tests.jlc") \
        .load()

    df.printSchema()

    # Transform

    # Sink
    query = df.writeStream \
        .format('console') \
        .outputMode('update') \
        .start()

    query.awaitTermination()
