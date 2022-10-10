import pendulum
from airflow.decorators import dag, task
from urllib import request
from datetime import timedelta
from helpers import run


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2022, 9, 1, tz="UTC"),
    catchup=False,
    tags=['bigdata-lab'],
)
def wikimedia_data_pipeline():
    """
    Data pipeline to consume and process data from wikimedia using Spark
    """
    @task()
    def download_data(execution_date=None):
        # Publishing pageviews data sometimes takes up to 2 hours
        download_date = execution_date - timedelta(hours=2)
        year, month, day, hour, *_ = download_date.timetuple()
        url = (
            "https://dumps.wikimedia.org/other/pageviews/"
            f"{year}/{year}-{month:0>2}/"
            f"pageviews-{year}{month:0>2}{day:0>2}-{hour:0>2}0000.gz"
        )
        # When we run locally on the airflow container we will store it in /opt/airflow/data
        #output_file = "/opt/airflow/data/wikipageviews-{year}{month:0>2}{day:0>2}{hour:0>2}.gz"
        #request.urlretrieve(url, output_file)

        # When we run remotely we have to create the data directory first in
        # the target machine
        output_file = f"pageviews-{year}-{month:0>2}-{day:0>2}-{hour:0>2}.gz"
        stdout, stderr = run(f"cd data && curl -o {output_file} {url}", host='hadoop.cesga.es', user='curso800')
        print(stdout, stderr)
        return output_file

    @task()
    def uncompress_data(filename, execution_date=None):
        # Publishing pageviews data sometimes takes up to 2 hours
        stdout, stderr = run(f"cd data && gunzip {filename}", host='hadoop.cesga.es', user='curso800')
        print(stdout, stderr)
        return filename.replace('.gz', '')

    # We can not retry upload to HDFS because it will fail if file exists
    @task(retries=0)
    def upload_to_hdfs(filename, execution_date=None):
        stdout, stderr = run(f"cd data && hdfs dfs -put {filename}", host='hadoop.cesga.es', user='curso800')
        print(stdout, stderr)
        return filename

    # We can not retry upload to HDFS because it will fail if file exists
    @task(retries=0)
    def process_in_spark(filename, execution_date=None):
        stdout, stderr = run(f"spark-submit process_wikimedia_pagecounts.py {filename}", host='hadoop.cesga.es', user='curso800')
        print(stdout, stderr)
        # If we return stdout we can see it in XComs easier than looking at the task log
        return stdout

    process_in_spark(upload_to_hdfs(uncompress_data(download_data())))

dag = wikimedia_data_pipeline()
