import json
import pendulum
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator

@dag(
    description='Example of how to combine decorated and traditional tasks',
    schedule="@daily",
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=['bigdata-lab'],
)
def combining_decorated_and_traditional_tasks():
    get_results_task = BashOperator(
        task_id='get_results',
        bash_command="""echo '{"results": [1, 2, 5]}'""",
        do_xcom_push=True,
    )

    @task()
    def process_results(results):
        results = json.loads(results)
        total = sum(results["results"])
        print(f"Total is {total}")
        return total

    processed_results = process_results(results=get_results_task.output)

combining_decorated_and_traditional_tasks()
