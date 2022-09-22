# Running pyspark locally
## Java
As a pre-requisite you will need Java, in case of Spark 2.4.0 you can use openjdk 8
```
apt install openjdk-8-jre
```
For newer versions you can use Java JDK 11, openjdk is fine but you can also use Amazon Corretto 11.

## Installing pyspark
When you are developing sometimes it is useful to test your program in your local machine.

To do this you just need to install `pyspark` and you can use spark local mode to run your application.

It is important that you choose a spark version that corresponds to the one that you will later on use in production.
It is also recommended to create a virtual environment first so you can more easily manage different dependency versions.
```
python3 -m venv venv
. venv/bin/activate
pip install pyspark==2.4.0
```

If you are using the Anaconda distribution you can install it with:
```
conda install pyspark=2.4.0
```

## Running pyspark
Now we can run pyspark in local mode:
```
pyspark --master local[3]
```

We can indicate how many workers to create, for example:
- `local[3]`: Run Spark locally with 3 worker threads (1 of them will be used for the driver)
- `local[*]`: Run Spark locally with as many worker threads as logical cores on your machine.

## Running an application
To run an application you can simply launch the script directly (there is no need to use `spark-submit` in this case):
```
python wordcount_local_mode.py
```
You can set the number of worker threads to use inside the script using a code similar to this:
```
    spark = SparkSession\
        .builder \
        .appName("WordCount") \
        .master("local[3]") \
        .getOrCreate()
```


It is also perfectly fine to use `spark-submit` as you would do in a cluster but indicating local mode:
```
spark-submit --master local[3] wordcount_local_mode.py
```

## Exercise
Lab 1: Install pyspark and run `wordcount_local_mode.py` in local mode.


