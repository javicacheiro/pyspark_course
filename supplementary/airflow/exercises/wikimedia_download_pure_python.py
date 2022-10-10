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
def wikimedia_download_pure_python():
    """
    Data pipeline to consume and process data from wikimedia
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
        output_path = f"/opt/airflow/data/pageviews-{year}{month:0>2}{day:0>2}{hour:0>2}.gz"
        request.urlretrieve(url, output_path)

    download_data()

dag = wikimedia_download_pure_python()
