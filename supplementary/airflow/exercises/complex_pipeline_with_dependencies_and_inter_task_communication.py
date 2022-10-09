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
def complex_pipeline_with_inter_task_communication_dag():
    """
    Example of a Data pipeline with dependencies and inter-task communication
    """
    @task()
    def download_dataset():
        stdout, stderr = run('sleep 5 && echo data1')
        print(stdout)

    @task()
    def compute_property_1():
        time.sleep(2)
        return 2.5

    @task()
    def compute_property_2():
        time.sleep(5)
        return 5.0

    @task()
    def compute_property_3():
        time.sleep(1)
        return 2.5

    @task()
    def generate_summary(p1, p2, p3):
        result = p1 + p2 + p3
        print('The result is:', result)

    download_dataset()
    generate_summary(compute_property_1(), compute_property_2(), compute_property_3())

    # If there was no interprocess communication we could write it like
    # donload_dataset() >> [compute_property_1(), compute_property_2(), compute_property_3()] >> generate_summary()


dag = complex_pipeline_with_inter_task_communication_dag()
