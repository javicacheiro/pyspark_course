import pendulum
from airflow.decorators import dag, task
import time
from helpers import run


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2022, 9, 1, tz="UTC"),
    catchup=False,
    tags=['bigdata-lab'],
)
def complex_pipeline_dag():
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
    def publish_to_internal_site_1():
        print('Publishing to internal site 1')

    @task()
    def publish_to_internal_site_2():
        print('Publishing to internal site 2')

    # NOTE: Airflow task dependencies can't handle [list] >> [list]
    #       so we have to split them over multiple lines
    #[download_dataset_1(), download_dataset_2(), download_dataset_3()] >> preprocess() >> [compute_properties_1(), compute_properties_2()] >> [publish_to_internal_site_1(), publish_to_internal_site_2()]

    # NOTE: If we do it this way, Airflow gets confused with the tasks generated from calling the functions, and it represents each compute_properties_1()and compute_properties_2() them as different tasks in the DAG
    #[download_dataset_1(), download_dataset_2(), download_dataset_3()] >> preprocess() >> [compute_properties_1(), compute_properties_2()]
    #compute_properties_1() >> [publish_to_internal_site_1(), publish_to_internal_site_2()]
    #compute_properties_2() >> [publish_to_internal_site_1(), publish_to_internal_site_2()]

    # This is the good way
    d1 = download_dataset_1()
    d2 = download_dataset_2()
    d3 = download_dataset_3()
    p = preprocess()
    c1 = compute_properties_1()
    c2 = compute_properties_2()
    p1 = publish_to_internal_site_1()
    p2 = publish_to_internal_site_2()

    [d1, d2, d3] >> p >> [c1, c2]
    c1 >> [p1, p2]
    c2 >> [p1, p2]


dag = complex_pipeline_dag()
