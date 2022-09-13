## Installing Kafka
Launch a VM: 
- Source: baseos-Rocky-8.5-v2
- Flavor: m1.large
- Networks: provnet-sisdevel-vlan-38

Install updates:
```
sudo dnf -y update
```

Create and attach a data volume to the instance. After that format it so we can use it:
```
mkfs.xfs -L $(hostname -s) /dev/vdb
mkdir /data
echo "LABEL=$(hostname -s)       /data   xfs     defaults        0 0" >> /etc/fstab
mount /data
```

Reboot the instance:
```
sudo reboot
```

Install Java JDK 11 (we will use Amazon Corretto 11)
```
sudo rpm --import https://yum.corretto.aws/corretto.key
sudo curl -L -o /etc/yum.repos.d/corretto.repo https://yum.corretto.aws/corretto.repo
sudo dnf install -y java-11-amazon-corretto-devel
```
Reference: https://docs.aws.amazon.com/corretto/latest/corretto-11-ug/generic-linux-install.html

Verify installation:
```
java -version
```

Download & Install Kafka:
- https://kafka.apache.org/downloads
- We will install the last kafka version compiled with scala 2.11 that is 2.4.1 Released March 12, 2020
```
curl -O https://archive.apache.org/dist/kafka/2.4.1/kafka_2.11-2.4.1.tgz
tar xzvf kafka_2.11-2.4.1.tgz
```
- Alternatively if we we want to be in the bleeding edge we can download the latest version:
```
curl -O https://downloads.apache.org/kafka/3.2.1/kafka_2.12-3.2.1.tgz
tar xzvf kafka_2.12-3.2.1.tgz
```

Create data directories:
```
sudo mkdir /data/zookeeper
sudo mkdir /data/kafka-logs

sudo chown $USER /data/zookeeper
sudo chown $USER /data/kafka-logs
```

Move to the kakfa directory:
```
# If you installed kafka version 2.4.1
cd kafka_2.11-2.4.1
# If you installed kafka version 3.2.1
cd kafka_2.12-3.2.1
```

Configure zookeeper data storage directory editting config/zookeeper.properties:
```zookeeper.properties
dataDir=/data/zookeeper
```

Start zookeeper:
```
./bin/zookeeper-server-start.sh config/zookeeper.properties
```

If everything went fine run it in daemon mode:
```
./bin/zookeeper-server-start.sh -daemon config/zookeeper.properties
```

Log are in:
- logs/zookeeper.out
- logs/server.log

Configure kafka broker data storage directory editting config/server.properties:
```server.properties
log.dirs=/data/kafka-logs
```

Check the IP address of the host:
```
ip address show
```

Configure kafka broker to advertise this address to clients instead of its hostname (external clients would not be able to resolve it):
```
advertised.listeners=PLAINTEXT://10.38.28.103:9092
```
See: https://www.confluent.io/blog/kafka-listeners-explained/

Start kafka broker:
```
bin/kafka-server-start.sh config/server.properties
```
If everything went fine run it in daemon mode:
```
bin/kafka-server-start.sh -daemon config/server.properties
```

Logs are in:
- logs/kafkaServer.out
- logs/server.log
- logs/controller.log
- logs/*

## Gracefully stopping the services
First stop the kafka broker
```
bin/kafka-server-stop.sh
```
Then stop zookeeper
```
bin/zookeeper-server-stop.sh
```
