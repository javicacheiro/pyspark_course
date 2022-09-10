"""
Reads streaming data from the given TCP socket and
prints the dataframe generated that acts like an
unbounded table.

## Creating the TCP server

You can create the listening TCP socket using netcat:

    nc -l -k <port>

where <port> is the port where you want netcat to listen.

## Usage

To submit the application use:

    module load anaconda3
    spark-submit Unit_8_spark_streaming-unbounded_table.py <hostname> <port>

where <hostname> and <port> are the address and port of the TCP socket.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split, expr
import sys

def parse_args():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <hostname> <port>")
        sys.exit(1)
    return (sys.argv[1], int(sys.argv[2]))


if __name__ == "__main__":
    host, port = parse_args()

    spark = SparkSession.builder \
        .appName("StructuredStreamingUnboundedTable") \
        .config('spark.dynamicAllocation.enabled', False) \
        .getOrCreate()

    # Each input line read from the stream is mapped to a row in the DataFrame
    # and the text is included inside a column named `value`
    lines = spark.readStream \
        .format('socket') \
        .option('host', host) \
        .option('port', port) \
        .load()

    # Start running the query
    query = lines.writeStream \
        .format('console') \
        .outputMode('complete') \
        .start()

    query.awaitTermination()
