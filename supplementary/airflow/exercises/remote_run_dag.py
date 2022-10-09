import pendulum
from airflow.decorators import dag, task
from helpers import run


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2022, 9, 1, tz="UTC"),
    catchup=False,
    tags=['bigdata-lab'],
)
def remote_run_dag():
    """
    Data pipeline to consume and process data from wikimedia
    """
    @task()
    def local_task():
        stdout, stderr = run('/bin/hostname')
        print('Local task stdout:', stdout)
        return stdout

    @task()
    def remote_task():
        stdout, stderr = run('/bin/hostname', host='hadoop.cesga.es', user='curso800')
        print('Remote task stdout:', stdout)
        return stdout

    local_task()
    remote_task()


dag = remote_run_dag()
