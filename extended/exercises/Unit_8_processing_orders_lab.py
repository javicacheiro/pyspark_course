from __future__ import print_function
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, expr, to_json
from  pyspark.sql.types import StructType, StructField, LongType, StringType, ArrayType

if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("Order Processing") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .getOrCreate()

    schema = StructType([
        StructField("order_id", LongType()),
        StructField("created_at", StringType()),
        StructField("products", ArrayType(StructType([
            StructField("product_id", LongType()),
            StructField("count", LongType()),
        ]))),
        StructField("customer_id", LongType()),
    ])

    #raw = spark.read \
    raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "10.38.28.103:9092") \
        .option("subscribe", "orders") \
        .option("startingOffsets", "earliest") \
        .load()


    #print(raw.collect())

    values = raw.select(
        from_json(col("value").cast("string"), schema).alias("value"))

    #print(values.collect())

    exploded = values.selectExpr("value.order_id",
                                 "value.created_at",
                                 "explode(value.products) as product",
                                 "value.customer_id")

    #print(exploded.collect())

    flattened = exploded \
        .withColumn("product_id", expr("product.product_id")) \
        .withColumn("count", expr("product.count")) \
        .drop("product")

    #print(flattened.collect())

    products = flattened.select("order_id", "product_id", "count")

    #print(products.collect())


    # We can use a console sink for testing
    #product_writer = products.writeStream \
    #    .format("console") \
    #    .start()

    # When ready we use the real kafka sink
    kafka_df = products.selectExpr(
        "cast(order_id as string) as key",
        """to_json(
            named_struct(
                'order_id', order_id,
                'product_id', product_id,
                'count', count
            )
        ) as value""")

    # The key column is optional
    #kafka_df = products.selectExpr(
    #    """to_json(
    #        named_struct(
    #            'order_id', order_id,
    #            'product_id', product_id,
    #            'count', count
    #        )
    #    ) as value"""
    #)

    product_writer = kafka_df.writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "10.38.28.103:9092") \
        .option("topic", "manufacturing") \
        .queryName("MyProducts") \
        .outputMode("append") \
        .option("checkpointLocation", "orders_checkpoint_dir") \
        .trigger(processingTime="5 seconds") \
        .start()


    product_writer.awaitTermination()
