"""
# Streaming app

Reads streaming data from a rate source and writes to memory sink
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split, expr, spark_partition_id
import time

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
    df_with_partition = df.withColumn('partition', spark_partition_id())

    df_with_partition.printSchema()

    # Sink
    query = df_with_partition.writeStream \
        .format('memory') \
        .outputMode('append') \
        .queryName('mytable') \
        .start()

    spark.sql('select count(*) from mytable').show(truncate=False)

    time.sleep(5)

    spark.sql('select count(*) from mytable').show(truncate=False)

    time.sleep(5)

    spark.sql('select count(*) from mytable').show(truncate=False)

    query.stop()
