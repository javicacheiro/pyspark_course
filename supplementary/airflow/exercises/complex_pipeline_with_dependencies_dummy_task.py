import pendulum
from airflow.decorators import dag, task
from datetime import timedelta
import time
from helpers import run


@dag(
    schedule_interval=timedelta(minutes=5),
    start_date=pendulum.datetime(2022, 9, 1, tz="UTC"),
    catchup=False,
    tags=['bigdata-lab'],
)
def complex_pipeline_dummy_task_dag():
    """
    Example of a Data pipeline with dependencies
    """
    @task()
    def download_dataset_1():
        stdout, stderr = run('sleep 5 && echo "dataset2 downloaded"')
        print(stdout)

    @task()
    def download_dataset_2():
        stdout, stderr = run('sleep 3 && echo "dataset2 downloaded"')
        print(stdout)

    @task()
    def download_dataset_3():
        time.sleep(2)
        print('dataset3 downloaded')

    @task()
    def preprocess():
        time.sleep(1)
        print('Preprocessing')

    @task()
    def compute_properties_1():
        time.sleep(2)
        print('Processing')

    @task()
    def compute_properties_2():
        time.sleep(2)
        print('Processing')

    @task()
    def join():
        pass

    @task()
    def publish_to_internal_site_1():
        print('Publishing to internal site 1')

    @task()
    def publish_to_internal_site_2():
        print('Publishing to internal site 2')

    # NOTE: Airflow task dependencies can't handle [list] >> [list]
    #       so we have to split them over multiple lines
    #[download_dataset_1(), download_dataset_2(), download_dataset_3()] >> preprocess() >> [compute_properties_1(), compute_properties_2()] >> [publish_to_internal_site_1(), publish_to_internal_site_2()]

    [download_dataset_1(), download_dataset_2(), download_dataset_3()] >> preprocess() >> [compute_properties_1(), compute_properties_2()] >> join() >> [publish_to_internal_site_1(), publish_to_internal_site_2()]


dag = complex_pipeline_dummy_task_dag()
