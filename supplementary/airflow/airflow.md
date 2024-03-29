# Apache Airflow
```
1. Introduction
2. Airflow Architecture
3. APIs available
4. Defining workflows with the classic API
  4.1. Pipeline
  4.2. Operators
  4.3. Tasks
  4.4. Sharing data using XComs
5. Defining workflows with the new TaskFlow API
  5.1. Accessing context variables
6. Scheduling
7. Processing data incrementally
8. Backfilling
9. Datasets and Data-Aware Scheduling
10. Web Interface Walkthrough
11. Airflow CLI
12. Tips
13. References
```


## Introduction
Apache Airflow is a sort of *cron on asteroids*.

It is quite useful to define workflows that allow us to glue together the different steps of our data pipeline so that they will be scheduled periodically.

## Airflow Architecture
![Airflow Archictecture](http://bigdata.cesga.es/img/airflow_architecture.png)

From Airflow documentation we see that the basic Airflow components are:
- A **scheduler**, which handles both triggering scheduled workflows, and submitting Tasks to the executor to run.
- An **executor**, which handles running tasks. In the default Airflow installation, this runs everything inside the scheduler, but most production-suitable executors actually push task execution out to **workers**.
- A **webserver**, which presents a handy user interface to inspect, trigger and debug the behaviour of DAGs and tasks.
- A **folder of DAG files**, read by the scheduler and executor (and any workers the executor has)
- A **metadata database**, used by the scheduler, executor and webserver to store state.

## APIs available
There are tow APIs available in Airflow:
- The classical API based on operators
- The new TaskFlow API

## Defining workflows with the classic API
### Pipeline
Do you remember the DAG concept from Spark? Well, it is back.

A pipeline is just a Python script that defines a DAG in Airflow.
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    'etl_classic_api',
    default_args={
        'depends_on_past': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='A simple ETL using BashOperator',
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

    t1 >> t2 >> t3
```

Different tasks run on different workers at different points in time, which means that this script cannot be used to cross communicate between tasks. Note that for this purpose we have a more advanced feature called XComs. 

With the new TaskFlow API the usage of XComs is much less important.

### Operator
An operator is the classic way of working in Airflow. It helps to define one unit of work.

For example we have the BashOperator:
```
    t1 = BashOperator(
        task_id='print_date1',
        bash_command='date',
    )
```

### Tasks
Internally an `operator` is instantiated as a `task` that acts like a wrapper of our operator.

### Sharing data using XComs
Airflow allows us to share small pieces of data between tasks using XComs.

```
XComs (short for "cross-communications") are a mechanism that let Tasks talk to each other, as by default Tasks are entirely isolated and may be running on entirely different machines.

XComs are explicitly "pushed" and "pulled" to/from their storage using the xcom_push and xcom_pull methods on Task Instances. Many operators will auto-push their results into an XCom key called return_value if the do_xcom_push argument is set to True (as it is by default).
```


Let's see them in action using a ETL example from the Apache Airflow tutorial:
```python
import json
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG(
    'etl_classic_api',
    description='A simple ETL using Classic API',
    schedule="@daily",
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=['bigdata-lab'],
) as dag:
    def extract(**kwargs):
        ti = kwargs['ti']
        data_string = '{"1001": 301.27, "1002": 433.21, "1003": 502.22}'
        ti.xcom_push('order_data', data_string)

    def transform(**kwargs):
        ti = kwargs['ti']
        extract_data_string = ti.xcom_pull(task_ids='extract', key='order_data')
        order_data = json.loads(extract_data_string)
        total_order_value = 0
        for value in order_data.values():
            total_order_value += value
        total_value = {"total_order_value": total_order_value}
        total_value_json_string = json.dumps(total_value)
        ti.xcom_push('total_order_value', total_value_json_string)

    def load(**kwargs):
        ti = kwargs['ti']
        total_value_string = ti.xcom_pull(task_ids='transform', key='total_order_value')
        total_order_value = json.loads(total_value_string)
        print(total_order_value)

    extract_task = PythonOperator(
        task_id='extract',
        python_callable=extract,
    )

    transform_task = PythonOperator(
        task_id='transform',
        python_callable=transform,
    )

    load_task = PythonOperator(
        task_id='load',
        python_callable=load,
    )

    extract_task >> transform_task >> load_task
```

`ti` is a shorthand that refers to the `task_instance` object:
```python
ti = kwargs['ti']
```

We push a variable to make it available for other tasks using the `xcom_push` method:
```python
ti.xcom_push('total_order_value', total_value_json_string)
```

The we can read the variable pulling it with the `xcom_pull` method:
```python
total_value_string = ti.xcom_pull(task_ids='transform', key='total_order_value')
```


## Defining workflows with the new TaskFlow API
With the new TaskFlow API we can define tasks directly in a pythonic way using a python decorator.

```python
@task
def my_task():
    print("Hello")
```

It is also very easy to pass variables between tasks because they just work as if we were writing python code, so we do not need XComs.

Let's see the previous ETL pipeline example from the Apache Airflow tutorial re-written in the new TaskFlow API:
```python
import json
import pendulum
from airflow.decorators import dag, task

@dag(
    description='A simple ETL using TaskFlow',
    schedule="@daily",
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=['bigdata-lab'],
)
def etl_taskflow_api():
    @task()
    def extract():
        data_string = '{"1001": 301.27, "1002": 433.21, "1003": 502.22}'
        order_data_dict = json.loads(data_string)
        return order_data_dict

    @task(multiple_outputs=True)
    def transform(order_data_dict: dict):
        total_order_value = 0
        for value in order_data_dict.values():
            total_order_value += value
        return {"total_order_value": total_order_value}

    @task()
    def load(total_order_value: float):
        print(f"Total order value is: {total_order_value:.2f}")

    order_data = extract()
    order_summary = transform(order_data)
    load(order_summary["total_order_value"])

etl_taskflow_api()
```

NOTE:
- Setting `multiple_outputs=True` unrolls dictionaries, lists or tuples into separate XCom values. As an alternative, using the typing `Dict` for the function return type, the `multiple_outputs` parameter is automatically set to true.
```python
    @task()
    def transform(order_data_dict: dict) -> Dict[str, float]:
        total_order_value = 0
        for value in order_data_dict.values():
            total_order_value += value
        return {"total_order_value": total_order_value}
```

### Accessing context variables
In the new TaskFlow API there are different ways of accessing context variables.

- With explicit arguments (recommended). Just remember to set them as optional arguments with the default value None.
    ```python
    @task
    def my_task(execution_date=None, next_ds=None):
        print(execution_date, next_ds)
    ```
- With `kwargs`:
    ```python
    @task
    def my_task(**kwargs):
        execution_date = kwargs["execution_date"]
        next_ds = kwargs["next_ds"]
        print(execution_date, next_ds)
    ```
    I would recommend to rename `kwargs` as `context`:
    ```python
    @task
    def my_task(**context):
        execution_date = context["execution_date"]
        next_ds = context["next_ds"]
        print(execution_date, next_ds)
    ```
- With `get_current_context`. This can be used also in pure python functions that are not decorated as `@task`:
    ```python
    from airflow.operators.python import get_current_context
    def my_task():
        context = get_current_context()
        execution_date = context["execution_date"]
        next_ds = context["next_ds"]
        print(execution_date, next_ds)
    ```

### Combining TaskFlow tasks with traditional tasks
We can instantiate any `decorated task` created with the TaskFlow API and then use it as if it was a `traditional task`. This way we can combine it with any traditional tasks created from operators:
```python
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
```

NOTES:
- BashOperator: If `do_xcom_push` is set to True the last line written to stdout will be pushed to an XCom when the bash command completes.
- By default, using the `.output` property to retrieve an XCom result is a shorthand to:
    ```
    task_instance.xcom_pull(task_ids="my_task_id", key="return_value")
    ```

## Scheduling
We have different options to schedule DAG `jobs`:
- A preset Airflow schedule
- A cron expression
- A timedelta object
- A Timetable (new in Airflow 2.2)
- On updates to a dataset (new in Airflow 2.4)

Using preset Airflow schedules:
```python
schedule_interval="@daily"
```

| Preset | Meaning|
| ---    | ---    |
| @once  | Schedule just once |
| @hourly  | Schedule hourly at the beginning of the hour |
| @daily  | Schedule daily at midnight |
| @weekly  | Schedule weekly at midnight on Sunday |
| @monthly  | Schedule monthly on the first day of the month at midnight |
| @yearly  | Schedule yearly on Jan 1 at midnight |


Using a cron expression:
```
# ┌─────── minute (0 - 59)
# │ ┌────── hour (0 - 23)
# │ │ ┌───── day of the month (1 - 31)
# │ │ │ ┌───── month (1 - 12)
# │ │ │ │ ┌──── day of the week (0 - 6) (Sunday to Saturday;
# │ │ │ │ │      7 is also Sunday on some systems)
# * * * * *
```

```python
# hourly
schedule_interval="0 * * * *"
# daily
schedule_interval="0 1 * * *"
# twice per hour
schedule_interval="0,30 * * * *"
# each 5 minutes
schedule_interval="*/5 * * * *"
```
And there are much more prossibilities using cron expressions. You can review your cron-based expressions at:
- [Crontab guru](https://crontab.guru)

Using a timedelta object (frequency-based interval):
```
# Each 2 days
schedule_interval=dt.timedelta(days=2)
# Each 90 minutes
schedule_interval=dt.timedelta(minutes=90)
```

## Processing data incrementally
Airflow makes available to our tasks a series of variables, referred as **execution dates**, that allow us to process data incrementally:
- `execution_date`: it is a `timestamp` object that represents the start time of the schedule interval for which our DAG is being executed.
- `next_execution_date`: it is a `timestamp` object that represents the end time of the schedule interval.
- `previous_execution_date`: it is a `timestamp` object that represents the start of the previous schedule interval.

![Execution dates](http://bigdata.cesga.es/img/airflow_execution_dates.png)

We can use the python `strftime` method to convert them to the format we need in our tasks:
```python
execution_date.strftime('%d-%m-%Y')
```
or by using the following shortcuts:
- `ds`: execution_date formated as YYYY-MM-DD
- `ds_nodash`: execution_date formated as YYYYMMDD
- `next_ds`: execution_date formated as YYYY-MM-DD
- `next_ds_nodash`: execution_date formated as YYYYMMDD
- `execution_date.day`
- `execution_date.month`
- `execution_date.year`

## Backfilling
Airflow allows to define a `start_date` in the past for our DAG. This way it will run our DAG passing previous execution dates until it catches with the current time, this way it will load and analyze past data. This feature is called `backfilling`.

To make use of this feature it is critical that we program our tasks so they do not depend on current time but on variables like `execution_date` that are provided by Airflow (see previous section).

This feature is usually enabled by default, it can be disabled by setting `catchup=False` in our DAG or by setting `catchup_by_default=False` in the configuration file.

We can see the default value with:
```
airflow config get-value scheduler catchup_by_default
```
If there were no changes in the configuration, we will see that this is set to `True`.

So if we want to disable it in our DAG we have to set `catchup=False`:
```python
@dag(
    schedule_interval="@hourly",
    start_date=pendulum.datetime(2022, 9, 1, tz="UTC"),
    catchup=False,
    tags=['bigdata-lab'],
)
```

## Datasets and Data-Aware Scheduling
New in Airlflow 2.4 (2022-09-19)!

We can define datasets and use them to define dependencies between DAGs.

A DAG can be configured so it is only run when a dataset is updated.

## Web Interface Walkthrough

### DAGs
![Grid](http://bigdata.cesga.es/img/airflow_dags.png)

### Grid
![Grid](http://bigdata.cesga.es/img/airflow_grid.png)

### Graph
![Graph](http://bigdata.cesga.es/img/airflow_graph.png)

### Calendar
![Calendar](http://bigdata.cesga.es/img/airflow_calendar.png)

### Task Duration
![Task Duration](http://bigdata.cesga.es/img/airflow_task_duration.png)

### Task Tries
![Task Tries](http://bigdata.cesga.es/img/airflow_task_tries.png)

### Landing Times
![Landing Times](http://bigdata.cesga.es/img/airflow_landing_times.png)

From Maxime Beauchemin, the original creator of Apache Airflow:
```
Maxime Beauchemin @mistercrunch Jun 09 2016 11:12
it's the number of hours after the time the scheduling period ended
take a schedule_interval='@daily' run for 2016-01-01 that finishes at 2016-01-02 03:52:00
landing time is 3:52
```

### Gantt
![Gantt](http://bigdata.cesga.es/img/airflow_gantt.png)

### Details
![Details](http://bigdata.cesga.es/img/airflow_details.png)

### Code
![Code](http://bigdata.cesga.es/img/airflow_code.png)

### Audit Log
![Audit Log](http://bigdata.cesga.es/img/airflow_audit_log.png)

## Airflow CLI
Besides the convenient web interface, Airflow has also a powerful CLI interface.

Display cheat sheet

    airflow cheat-sheet

Show airflow version

    airflow version

Summary info about the airflow installation

    airflow info

View configuration

    airflow config list

Information about loaded plugins

    airflow plugins

Manage DAGs
```
airflow dags list                         | List all the DAGs
airflow dags list-import-errors           | List all the DAGs that have import errors
airflow dags list-jobs                    | List the jobs
airflow dags list-runs -d <DAG>           | List DAG runs given a DAG id
airflow dags next-execution <DAG>         | Get the next execution datetimes of a DAG
airflow dags pause <DAG>                  | Pause a DAG
airflow dags show <DAG>                   | Displays DAG's tasks with their dependencies
```

Manage jobs
```
airflow jobs check                        | Checks if job(s) are still alive
```

Manage tasks
```
airflow tasks list <DAG>                  | List the tasks within a DAG
airflow tasks clear <DAG>                 | Clear a set of task instance, as if they never ran
airflow tasks failed-deps                 | Returns the unmet dependencies for a task instance
airflow tasks render                      | Render a task instance's template(s)
airflow tasks run                         | Run a single task instance
airflow tasks state                       | Get the status of a task instance
airflow tasks states-for-dag-run          | Get the status of all task instances in a dag run
airflow tasks test <DAG> <task>           | Test a task instance
```

Manage users
```
airflow users add-role                    | Add role to a user
airflow users create                      | Create a user
airflow users delete                      | Delete a user
airflow users export                      | Export all users
airflow users import                      | Import users
airflow users list                        | List users
airflow users remove-role                 | Remove role from a user
```

## Tips
- DAGs take some time to load in the web interface, remember to refresh if auto-refresh is not enabled
- It also helps to look for the name of the new DAG in the search box
- Sometimes when you load a DAG in the DAGs folder it does not appear in the web interface this could be due to import errors
- Always look for import errors after adding new DAGs to the DAG folder:
```
airflow dags list-import-errors
```
- Import errors will also appear in the web interface in a message, but tend to be slow
- If you can choose, use the new TaskFlow API

## Exercises
- Lab 0: [Airflow installation](exercises/airflow_installation.md)
- Lab 1: [Simple DAG using BashOperator](exercises/dag_using_operators.py)
- Lab 2: ETL
 - Creating a simple ETL with the classic API: [ETL Classic API](exercises/etl_classic_api.py)
 - Creating a simple ETL with the TaskFlow API: [ETL TaskFlow API](exercises/etl_taskflow_api.py)
- Lab 3: Complex Pipeline Examples
  - Creating a complex pipeline with lots of dependencies: [Complex Pipeline with dependencies](exercises/complex_pipeline_with_dependencies.py)
  - Adding a dummy task as a join task: [Complex Pipeline with dependencies and a dummy task](exercises/complex_pipeline_with_dependencies_dummy_task.py)
  - Inter-task communication: [Complex Pipeline with dependencies and inter-task communication](exercises/complex_pipeline_with_dependencies_and_inter_task_communication.py)
- Lab 4: Running remote tasks
  - [Running remote tasks](exercises/running_remote_tasks.md)
  - [Remote run DAG](exercises/remote_run_dag.py)
- Lab 5: How to use context variables like `execution_date` to define DAGs
  - [wikimedia download using bashoperator](exercises/wikimedia_download_bashoperator.py)
      - We will trigger the DAG with an `execution_date` in the past
      - To do that trigger the DAG from the web interface with the `Trigger DAG w/ config` option and there we will indicate the logical date in the time box.
      - Alternatively,  from the CLI, we can also specify an `execution_date` in the past:
      ```
      ./airflow.sh dags trigger -e '2022-10-10T12:00:00' wikimedia_download_bashoperator
      ```
      this is due to the fact that wikimedia pageviews sometimes are delayed up to 2 hours.
  - [wikimedia download using pure python](exercises/wikimedia_download_pure_python.py)
      - In this second example we do the trick directly in the python code
- Lab 6: [Creating a data pipeline](exercises/creating_a_data_pipeline.md)
  - [Wikimedia pagecounts data pipeline that uses Spark for processing](exercises/wikimedia_data_pipeline.py)
  - [Spark Application to process wikimedia data](exercises/process_wikimedia_pagecounts.py)

## References
- [Fundamental Concepts](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/fundamentals.html)
- [Architecture Overview](https://airflow.apache.org/docs/apache-airflow/stable/concepts/overview.html)
- [Concepts](https://airflow.apache.org/docs/apache-airflow/stable/concepts/index.html)
- [XComs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/xcoms.html)
- [Working with TaskFlow](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html)
- [Scheduling and Timetables in Airflow](https://www.astronomer.io/guides/scheduling-in-airflow/)
- [Crontab guru](https://crontab.guru)
- [Cross-DAG Dependencies](https://www.astronomer.io/guides/cross-dag-dependencies/)
- [Datasets and Data-Aware Scheduling in Airflow](https://www.astronomer.io/guides/airflow-datasets/)
