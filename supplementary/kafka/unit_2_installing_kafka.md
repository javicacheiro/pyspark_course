## Installing Kafka

Pre-requisite: creating a ssh key pair:
- If you do not have one existing ssh key pair, you can create one in the hadoop cluster:
    ```
    ssh-keygen -t rsa
    ```
- Copy it to your PC
    ```
    scp cursoXXX@hadoop.cesga.es:.ssh/id_rsa.pub .
    ```

Launch a VM: 
- Instance name: kafka-cursoXXX
- Source: baseos-Rocky-8.5-v2
- Flavor: m1.medium
- Networks: provnet-formacion-vlan-133
- Security groups: default (already adjusted to allow connections)
- Key Pair:
  - Import Key Pair: 
    - Key Pair name: curso849
    - Key Type: SSH Key
    - Load Public Key from a file: the `id_rsa.pub` from the previous step

Look the `IP Address` assigned to the VM and Connect to the instance using SSH:
```
ssh cesgaxuser@<IP_address>
```

Install updates:
```
sudo dnf -y update
```

Create `data` dir:
```
sudo mkdir /data
```

OPTIONAL: Create and attach a data volume to the instance. After that format it so we can use it:
```
sudo -s
mkfs.xfs -L $(hostname -s) /dev/vdb
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
- We will be in the bleeding edge and we will download the 3.2.3 version:
```
curl -O https://archive.apache.org/dist/kafka/3.2.3/kafka_2.12-3.2.3.tgz
tar xzvf kafka_2.12-3.2.3.tgz
```
- Since our Spark installation is using scala 2.11, if we want to install the last kafka version compiled with scala 2.11 that is 2.4.1 Released March 12, 2020. NOTE: it is not required that spark and kafka are both compiled with scala 2.11:
```
curl -O https://archive.apache.org/dist/kafka/2.4.1/kafka_2.11-2.4.1.tgz
tar xzvf kafka_2.11-2.4.1.tgz
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
# If you installed kafka version 3.2.3
cd kafka_2.12-3.2.3
# If you installed kafka version 2.4.1
cd kafka_2.11-2.4.1
```

Configure zookeeper data storage directory editting `config/zookeeper.properties`:
```zookeeper.properties
dataDir=/data/zookeeper
```

Start zookeeper:
```
./bin/zookeeper-server-start.sh config/zookeeper.properties
```

If everything went fine (ie. you saw no error messages previously) run it in daemon mode:
```
./bin/zookeeper-server-start.sh -daemon config/zookeeper.properties
```

Log are in:
- logs/zookeeper.out
- logs/server.log

Configure kafka broker data storage directory editting `config/server.properties`:
```server.properties
log.dirs=/data/kafka-logs
```

Check the IP address of the host:
```
ip address show
```

Configure kafka broker to advertise this address to clients instead of its hostname (external clients would not be able to resolve it):
```
advertised.listeners=PLAINTEXT://10.133.X.Y:9092
```
See: https://www.confluent.io/blog/kafka-listeners-explained/

Start kafka broker:
```
./bin/kafka-server-start.sh config/server.properties
```
If everything went fine (ie. no errors) run it in daemon mode:
```
./bin/kafka-server-start.sh -daemon config/server.properties
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
