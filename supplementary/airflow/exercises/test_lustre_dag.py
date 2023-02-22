import pendulum
from datetime import timedelta
from airflow.decorators import dag, task
from helpers import run
from airflow.hooks.base import BaseHook
import requests

SLACK_CONN_ID = 'slack_cesga_monitoring_alerts'

def slack_alert(context):
    host = 'https://hooks.slack.com/services/'
    token = BaseHook.get_connection(SLACK_CONN_ID).password
    slack_webhook_url = host + token
    message = ':red_circle: Posible problema no Lustre scratch.'
    requests.post(slack_webhook_url, json={"text": str(message)})


@dag(
    schedule_interval="@hourly",
    start_date=pendulum.datetime(2023, 2, 22, tz="UTC"),
    catchup=False,
    on_success_callback=None,
    on_failure_callback=slack_alert,
    tags=['monitoring'],
)
def test_lustre_dag():
    """
    Data pipeline to test lustre
    """
    @task(execution_timeout=timedelta(seconds=300), retries=1)
    def test_lustrep_nlsas():
        stdout, stderr = run('monitoring-tests/test_lustrep_nlsas.sh', host='ft3.cesga.es', user='uscfajlc')
        print('Remote task stdout:', stdout)
        return stdout

    test_lustrep_nlsas()


dag = test_lustre_dag()
