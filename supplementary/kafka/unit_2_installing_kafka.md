# Installing Kafka

We will install Kafka in the cloud using OpenStack.

## Creating the virtual resources
### Creating a SSH key pair
If you do not have one existing ssh key pair, you can create one in the hadoop cluster:
```
ssh-keygen -t rsa
```

### Launching the server from the OpenStack Web Interface
Connect to:

    https://cloud.srv.cesga.es

In this case you will need the SSH public key that you generated previously, so copy it to your PC:
```
scp cursoXXX@hadoop.cesga.es:.ssh/id_rsa.pub .
```

Launch a new instance: 
- Instance name: kafka-cursoXXX
- Source: baseos-Rocky-8.7-v4
- Flavor: a1.2c4m
- Networks: provnet-formacion-vlan-133
- Security groups: kafka (already created to allow connections)
- Key Pair:
  - Import Key Pair: 
    - Key Pair name: cursoXXX
    - Key Type: SSH Key
    - Load Public Key from a file: the `id_rsa.pub` you downloaded from the previous step

### Launching the server using the OpenStack CLI
We can alternatively use the OpenStack CLI so we have all the power of the command line.

The openstack CLI is available in `hadoop.cesga.es` as a module so we can use it from there:
```bash
# Load the openstack module
module load openstack
# Enable bash completion
source /opt/cesga/openstack/osc.bash_completion
# First provide your credentials and the project name
source /opt/cesga/openstack/interactive-openrc.sh
# Create a keypair
openstack keypair create --public-key ~/.ssh/id_rsa.pub cursoXXX
# Create the server
openstack server create --boot-from-volume 80 --image baseos-Rocky-8.7-v4 --flavor a1.2c4m --key-name cursoXXX --network provnet-formacion-vlan-133 --security-group kafka kafka-cursoXXX
# The new server will appear in the list of active servers
openstack server list
```

## Connecting to the server
Look the `IP Address` assigned to the VM and Connect to the instance using SSH:
```bash
ssh cesgaxuser@<IP_address>
```

## Optional: Installing updates
Install updates:
```bash
sudo dnf -y update
```

Reboot the instance:
```
sudo reboot
```

## Adding storage for Kafka
We will use a dedicated data volume to storage Kakfa data.

- Create `data` dir:
```bash
sudo mkdir /data
```

- In the OpenStack web or using the CLI, create a volume:
```bash
openstack volume create --size 100 kafka-cursoXXX-data
openstack server add volume kafka-cursoXXX kafka-cursoXXX-data
```

- Format and mount it:
```bash
sudo mkfs.xfs -L kafka-data /dev/vdb
sudo bash -c 'echo "LABEL=kafka-data       /data   xfs     defaults        0 0" >> /etc/fstab'
sudo mount /data
```


## Installing Java
Install Java JDK 11 (we will use Amazon Corretto 11)
```
sudo rpm --import https://yum.corretto.aws/corretto.key
sudo curl -L -o /etc/yum.repos.d/corretto.repo https://yum.corretto.aws/corretto.repo
sudo dnf install -y java-11-amazon-corretto-devel
```

Verify installation:
```
java -version
```

Reference: [Corretto 11 Installation](https://docs.aws.amazon.com/corretto/latest/corretto-11-ug/generic-linux-install.html)

## Installing Kafka
### Download Kafka:
- https://kafka.apache.org/downloads
- We will download the 3.7.1 version:
```
curl -O https://archive.apache.org/dist/kafka/3.7.1/kafka_2.13-3.7.1.tgz
tar xzvf kafka_2.13-3.7.1.tgz
```
NOTE: Since our Spark installation is using scala 2.11, if we want to install the last kafka version compiled with scala 2.11 that is 2.4.1 Released March 12, 2020. NOTE: it is not required that spark and kafka are both compiled with scala 2.11:
```
curl -O https://archive.apache.org/dist/kafka/2.4.1/kafka_2.11-2.4.1.tgz
tar xzvf kafka_2.11-2.4.1.tgz
```

Move to the kakfa directory to configure and run Kafka:
```
cd kafka_2.13-3.7.1
```

### Option 1: Configuring Kafka in KRaft mode
Create the data storage directories:
```bash
sudo mkdir /data/kraft-combined-logs
sudo chown $USER /data/kraft-combined-logs
```

Configure KRaft data storage directory editting `config/kraft/server.properties`:
```config/kraft/server.properties
log.dirs=/data/kraft-combined-logs
```

Format the storage for KRaft:
```bash
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties
```

Check the IP address of the host:
```
hostname -i
```

Configure kafka broker to advertise this address to clients instead of its hostname (external clients would not be able to resolve it):
```
advertised.listeners=PLAINTEXT://10.X.Y.Z:9092
```
See: https://www.confluent.io/blog/kafka-listeners-explained/

Start kafka broker:
```
./bin/kafka-server-start.sh config/kraft/server.properties
```
If everything went fine (ie. no errors) run it in daemon mode:
```
./bin/kafka-server-start.sh -daemon config/kraft/server.properties
```

We can see that only the Kafka process is running and no Zookeeper server is needed:
```
jps
```

Logs are in:
- logs/kafkaServer.out
- logs/server.log
- logs/controller.log
- logs/*

### Option 2: Configuring Kafka in Zookeeper mode
Create the data storage directories:
```bash
sudo mkdir /data/zookeeper
sudo mkdir /data/kafka-logs

sudo chown $USER /data/zookeeper
sudo chown $USER /data/kafka-logs
```

#### Zookeeper
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

#### Kafka Broker
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
advertised.listeners=PLAINTEXT://10.X.Y.Z:9092
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

At this point we will have two processed running Zookeeper and Kafka, we can verify that with:
```
jps
```

Logs are in:
- logs/kafkaServer.out
- logs/server.log
- logs/controller.log
- logs/*

## Gracefully stopping the services
First stop the kafka broker:
```
bin/kafka-server-stop.sh
```
If in zookeeper mode, after that stop zookeeper:
```
bin/zookeeper-server-stop.sh
```
