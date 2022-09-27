from __future__ import print_function
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, expr, to_json, window, expr, to_timestamp, lit, udf
from pyspark.sql.types import StructType, StructField, LongType, StringType, ArrayType, DoubleType
from textblob import TextBlob


if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("Twitter Sentiment Analysis") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .getOrCreate()

    # SOURCE
    schema = StructType([
        StructField("created_at", StringType()),
        StructField("lang", StringType()),
        StructField("text", StringType()),
    ])

    raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "10.38.28.103:9092") \
        .option("subscribe", "twitter") \
        .option("startingOffsets", "earliest") \
        .load()

    # TRANSFORM
    values = raw.select(
        from_json(col("value").cast("string"), schema).alias("value"))

    exploded = values.selectExpr("value.*")

    tweets = exploded.withColumn(
        "created_at",
        to_timestamp(col("created_at"), "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")
    )

    # We will now load our sentiment analysis model using TextBlob
    @udf(returnType=DoubleType())
    def polarity(text):
            return sum([s.polarity for s in TextBlob(text).sentences])

    df = tweets.withColumn('polarity', polarity(col('text')))
    with_predictions = df.select('created_at', 'text', 'polarity')

    tumbling_window = with_predictions.groupBy(
        window(col("created_at"), "5 minutes")
    ).avg('polarity')

    # SINK
    sink = tumbling_window.writeStream \
        .format("console") \
        .outputMode("update") \
        .trigger(processingTime="5 seconds") \
        .option("truncate", "false") \
        .start()

    sink.awaitTermination()
