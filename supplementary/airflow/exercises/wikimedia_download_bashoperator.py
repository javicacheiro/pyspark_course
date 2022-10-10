import pendulum
from airflow.decorators import dag
from airflow.operators.bash import BashOperator


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2022, 9, 1, tz="UTC"),
    catchup=False,
    tags=['bigdata-lab'],
)
def wikimedia_download_bashoperator():
    """
    Data pipeline to consume and process data from wikimedia

    NOTE: Publishing pageviews data sometimes takes up to 2 hours
          so set execution_date 2 hours in the past

    Trigger it from the CLI:

        ./airflow.sh dags trigger -e '2022-10-10T12:00:00' wikimedia_download_bashoperator

    Or from the web interface with the trigger with config and indicate the logical date in the time box.
    """
    download_data = BashOperator(
        task_id="download_data",
        bash_command=(
            "cd /opt/airflow/data && "
            "curl -o pageviews-"
            "{{ execution_date.year }}"
            "{{ '{:02}'.format(execution_date.month) }}"
            "{{ '{:02}'.format(execution_date.day) }}-"
            "{{ '{:02}'.format(execution_date.hour) }}0000.gz "
            "https://dumps.wikimedia.org/other/pageviews/"
            "{{ execution_date.year }}/"
            "{{ execution_date.year }}-{{ '{:02}'.format(execution_date.month) }}/"
            "pageviews-{{ execution_date.year }}"
            "{{ '{:02}'.format(execution_date.month) }}"
            "{{ '{:02}'.format(execution_date.day) }}-"
            "{{ '{:02}'.format(execution_date.hour) }}0000.gz"
            ),
    )

    download_data

dag = wikimedia_download_bashoperator()
