## Using Kafka from Spark
Verify the scala version of our Spark installation running `spark-shell`:
```
[jlopez@cdh61-login3 ~]$ spark-shell
Spark context Web UI available at http://cdh61-login3.bd.cluster.cesga.es:4040
Spark context available as 'sc' (master = yarn, app id = application_1650627462529_4948).
Spark session available as 'spark'.
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 2.4.0-cdh6.1.1
      /_/

Using Scala version 2.11.12 (Java HotSpot(TM) 64-Bit Server VM, Java 1.8.0_191)
Type in expressions to have them evaluated.
Type :help for more information.

scala>
```
As we can see in our case with have spark 2.4.0-cdh6.1.1 compiled with scala 2.11.12.

To use kafka with spark we have to download the required connector from the maven repository:
- https://mvnrepository.com/search?q=org.apache.spark&p=2

For structured streaming we have to look for:
- spark-sql-kafka-0-10: Kafka 0.10+ Source For Structured Streaming
- https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10

For the old DStream API we would look for:
- spark-streaming-kafka-0-10: Spark Integration For Kafka 0.10

We locate the connector corresponding to our spark and scala version, in our case spark 2.4.0 and scala 2.11.
- https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10_2.11/2.4.0

In this page we look for the groupId, artifactId and version:
```
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-sql-kafka-0-10_2.11</artifactId>
    <version>2.4.0</version>
    <scope>test</scope>
</dependency>
```

Then to use it we just have to pass the groupId, artifactId and version to the `--packages` option of `spark-submit` as `--packages groupId:artifactId:version` and it will download automatically the jar file:
```
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 Unit_8_orders_kakfa.py
```

Reference:
- https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html
