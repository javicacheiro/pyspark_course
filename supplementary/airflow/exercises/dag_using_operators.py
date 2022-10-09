from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    'dag_using_operators',
    default_args={
        'depends_on_past': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='A simple DAG using BashOperator',
    schedule=timedelta(days=1),
    start_date=datetime(2022, 10, 1),
    catchup=False,
    tags=['bigdata-lab'],
) as dag:

    t1 = BashOperator(
        task_id='print_date1',
        bash_command='date',
    )

    t2 = BashOperator(
        task_id='sleep',
        depends_on_past=False,
        bash_command='sleep 5',
        retries=3,
    )

    t3 = BashOperator(
        task_id='print_end',
        depends_on_past=False,
        bash_command='echo "We have reached the end"',
    )

    t4 = BashOperator(
        task_id='print_date4',
        bash_command='date',
    )

    t1 >> [t2, t3] >> t4
