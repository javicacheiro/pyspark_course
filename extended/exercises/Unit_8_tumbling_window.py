from __future__ import print_function
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, expr, to_json, window, expr, to_timestamp
from  pyspark.sql.types import StructType, StructField, LongType, StringType, ArrayType

if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("Tumbling Window") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .getOrCreate()

    # SOURCE
    schema = StructType([
        StructField("order_id", LongType()),
        StructField("created_at", StringType()),
    ])

    raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "10.38.28.103:9092") \
        .option("subscribe", "tumbling.curso800") \
        .option("startingOffsets", "latest") \
        .load()

    # TRANSFORM
    values = raw.select(
        from_json(col("value").cast("string"), schema).alias("value"))

    exploded = values.selectExpr("value.*")

    orders = exploded.withColumn(
        "created_at",
        to_timestamp(col("created_at"), "yyyy-MM-dd HH:mm:ss")
    )

    tumbling_window = orders.groupBy(
        window(col("created_at"), "10 minutes")
    ).count()


    # SINK
    sink = tumbling_window.writeStream \
        .format("console") \
        .outputMode("update") \
        .trigger(processingTime="5 seconds") \
        .option("truncate", "false") \
        .start()

    sink.awaitTermination()
