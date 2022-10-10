# Creating a data pipeline
## Setup
In the airflow instance:
```
ssh-keygen -t rsa
ssh-copy-id cursoXXX@dtn.srv.cesga.es
ssh-copy-id cursoXXX@hadoop.cesga.es
```

Verify access:
```
ssh cursoXXX@dtn.srv.cesga.es
ssh cursoXXX@hadoop.cesga.es
```

Copy keys so they are available in the container:
```
cp -a .ssh/id_rsa* dags/keys/
```

## Wikimedia Data Format
Wikimedia **pageviews** dataset:
- [Analytics Datasets: Pageviews](https://dumps.wikimedia.org/other/pageviews/readme.html)
- [Technical documentation of the pageviews dataset](https://wikitech.wikimedia.org/wiki/Analytics/Data_Lake/Traffic/Pageviews)


## Copy the Spark program to the cluster
```
scp process_wikimedia_pagecounts.py curso800@hadoop.cesga.es:
```

## Create the required dirs in the remote servers
DTN:
```
mkdir data
```
Hadoop:
```
mkdir data
```
For this example we will store the files in the user home of HDFS, for production we would create a dedicated dir in HDFS.

## Load the Pipeline
```
scp wikimedia_data_pipeline.py cesgaxuser@airflow:dags/
```

If you do not see the new DAG verify that there were no import errors:
```
./airflow.sh dags list-import-errors
```

You can see the list of DAGs from the CLI:
```
./airflow.sh dags list
```

If the web interface does not display it but it appears in the CLI try searching for the name of the DAG in the "Search DAGs" box.

## Launch the pipeline
Go to the web interface and launch the pipeline.
