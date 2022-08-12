#!/bin/bash

#source /etc/profile.d/oracle-jdk.sh
export JAVA_HOME=/usr/jdk64/jdk1.8.0_60
export JRE_HOME=${JAVA_HOME}/jre
export PATH=${JAVA_HOME}/bin:${JAVA_HOME}/jre/bin:$PATH

#source /etc/profile.d/spark.sh
export PYSPARK_DRIVER_PYTHON="/opt/Anaconda2-4.1.1/bin/python"
export PYSPARK_PYTHON="/opt/Anaconda2-4.1.1/bin/python"
# Fix warn about spark being unable to load native-hadoop
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$JAVA_HOME/jre/lib/amd64/server/:/usr/hdp/2.4.2.0-258/hadoop/lib/native/


PKGS_DIR="/home/cesga/jlopez/local/lib"
#APP_DIR="/home/cesga/jlopez/notebooks/spark_streaming"
APP_DIR="/home/cesga/jlopez/ssh-attack-detector"

env

spark-submit --master yarn --deploy-mode cluster --packages com.databricks:spark-avro_2.10:2.0.1 --jars ${PKGS_DIR}/spark-streaming-kafka-assembly_2.10-1.6.1.2.4.2.0-258.jar --py-files ${PKGS_DIR}/avro-1.8.1-py2.7.egg --name 'SSH attack detector' --conf spark.dynamicAllocation.enabled=false --num-executors 2 --queue ops ${APP_DIR}/ssh_attack_detector.py
