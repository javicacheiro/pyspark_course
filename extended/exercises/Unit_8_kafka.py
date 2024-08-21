"""Streaming app: reads streaming data from a kafka topic

Reads configuration from the following environmental variables:
    - BROKER: Kafka Broker, it can include port eg. "10.38.28.103:9092"
    - TOPIC: Kafka Topic to read

"""
from pyspark.sql import SparkSession
import os

broker = os.environ['BROKER']
topic = os.environ['TOPIC']


if __name__ == '__main__':

    spark = SparkSession.builder \
        .appName('StreamingFromKafka') \
        .config('spark.sql.shuffle.partitions', 3) \
        .config('spark.streaming.stopGracefullyOnShutdown', 'true') \
        .config('spark.sql.streaming.schemaInference', 'true') \
        .getOrCreate()

    # Source
    df = spark.readStream \
        .format('kafka') \
        .option("kafka.bootstrap.servers", broker) \
        .option("subscribe", topic) \
        .load()

    df.printSchema()

    # Transform

    # Sink
    query = df.writeStream \
        .format('console') \
        .outputMode('update') \
        .start()

    query.awaitTermination()
