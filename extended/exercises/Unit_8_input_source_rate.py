"""
# Streaming app

Reads streaming data from a rate source
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split, expr
from pyspark.sql.functions import spark_partition_id

if __name__ == "__main__":

    spark = SparkSession.builder \
        .appName('StreamingFromRateSource') \
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
    df_with_partition_id = df.withColumn('partition', spark_partition_id())


    # Sink
    query = df_with_partition_id.writeStream \
        .format('console') \
        .option('truncate', 'false') \
        .outputMode('update') \
        .start()

    query.awaitTermination()
