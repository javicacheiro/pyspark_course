from __future__ import print_function
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, expr, to_json, window, expr, to_timestamp, lit
from pyspark.sql.types import StructType, StructField, LongType, StringType, ArrayType
from pyspark.ml import PipelineModel


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

    # We will now load our sentiment analysis model from the amazon reviews lab
    my_saved_model = PipelineModel.load('models/amazon_sentiment_analysis_cv_model')

    df = tweets.withColumn('reviewText', col('text')).withColumn('overall', lit(5.0))
    with_predictions = my_saved_model.transform(df).select('created_at', 'text', 'prediction')

    tumbling_window = with_predictions.groupBy(
        window(col("created_at"), "5 minutes")
    ).avg('prediction')

    # SINK
    sink = tumbling_window.writeStream \
        .format("console") \
        .outputMode("update") \
        .trigger(processingTime="5 seconds") \
        .option("truncate", "false") \
        .start()

    sink.awaitTermination()
