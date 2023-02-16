# Running remote tasks
To run remote tasks we can use a remote Airflow worker that is deployed in the node where we want to run the task, in a similiar way as we would do in other tools like Jenkins.

But there are times where we can not deploy software in the remote system or we prefer no to do it. In this case we can use the procedure that we will explore in this lab that **requires only SSH access to the remote system**.

## Setting up the connection to the remote system
First we will create a pair of SSH keys in the airflow machine:
```
ssh-keygen -t rsa
```
Then we will copy the private key to the `dags/keys` directory where the `run` function will look for it:
```
mkdir ~/dags/keys
cp -a ~/.ssh/ir_rsa ~/dags/keys
```

Finally we will grant access to the remote servers we want to connect to:
```
ssh-copy-id curso800@hadoop.cesga.es
```

We will repeat the last step for each of the remote servers we will be running tasks on.

Notice that the commands are launched from the container that runs the executor (airflow-worker) not from the host.

## Running remote tasks
The to run remote tasks we will make use of the `run` method in our `helpers.py` module:

```python
    @task()
    def remote_task():
        stdout, stderr = run('/bin/hostname', host='hadoop.cesga.es', user='curso800')
        print('Remote task stdout:', stdout)
        return stdout

```

Just in case, the same function also allows running local tasks:
```python
    @task()
    def local_task():
        stdout, stderr = run('/bin/hostname')
        print('Local task stdout:', stdout)
        return stdout
```

Take a look at the [Remote run DAG example](remote_run_dag.py) to see it in action.
