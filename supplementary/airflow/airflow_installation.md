# Airflow

## Installation
Copy the docker.repo file to the instance
```
scp docker.repo cesgaxuser@airflow:
```
Update the instance:
```
sudo dnf -y update
```
Install docker and docker-compose:
```
sudo cp docker.repo /etc/yum.repos.d
sudo dnf install -y --enablerepo docker docker-ce docker-compose-plugin
sudo systemctl enable docker
```
Reboot the instance:
```
sudo reboot
```

Check that docker is working:
```
sudo docker ps
# docker-compose-plugin: it is available as "docker compose" instead of "docker-compose"
sudo docker compose version
```

Fetch the Airflow deployment file for docker-compose:
```
curl -LfO https://airflow.apache.org/docs/apache-airflow/2.4.0/docker-compose.yaml
```

It will deploy the following services:
- airflow-scheduler: The scheduler monitors all tasks and DAGs, then triggers the task instances once their dependencies are complete.
- airflow-webserver: The webserver is available at http://localhost:8080.
- airflow-worker: The worker that executes the tasks given by the scheduler.
- airflow-init: The initialization service.
- postgres: the database
- redis: to forward messages from scheduler to workers

Directories shared with the containers (docker volumes):
- ./dags: where we will place our DAG files
- ./logs: the logs from task execution and scheduler.
- ./plugins: for our custom plugins

Additionally we will edit `docker-compose.yaml` and add a new volume to store data:
```
    volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
    - ./data:/opt/airflow/data
```


### Initializing the environment:
```
mkdir -p ./dags ./logs ./plugins ./data
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

### Initializing the database
```
sudo docker compose up airflow-init
```
The account created has the login airflow and the password airflow.

### Starting airflow
```
sudo docker compose up -d
```

We will see that the containers are now running:
```
sudo docker ps
```

### Running CLI commands
First install airflow.sh helper script:
```
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.4.0/airflow.sh'
chmod +x airflow.sh
```

Edit `airflow.sh` and replace `docker-compose run` by `sudo docker compose run`:
```bash
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

set -euo pipefail

export COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yaml"
if [ $# -gt 0 ]; then
    exec sudo docker compose run --rm airflow-cli "${@}"
else
    exec sudo docker compose run --rm airflow-cli
fi
```


Now simply run:
```
./airflow.sh info
# Enter a bash shell in the container
./airflow.sh bash
# Enter a pyton interpreter in the container
./airflow.sh python
```

### Accessing the web interface
The webserver is available at: http://airflow:8080.

The default account has the login airflow and the password airflow.


### Stopping the services
```
sudo docker compose down
```

### Cleaning up
```
docker-compose down --volumes --remove-orphans
# Be sure to save what you want before removing these dirs
rm -rf dags logs plugins data
```


Reference:
- [Running Airflow in Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
