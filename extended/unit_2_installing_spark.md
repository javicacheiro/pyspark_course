# Installing Spark

Launch a VM: 
- Source: baseos-Rocky-8.5-v2
- Flavor: m1.medium
- Networks: provnet-sisdevel-vlan-38
- Security group: spark (create first)

Add the addresses to /etc/hosts in all instances:
```
# spark deployment on openstack
10.38.28.231 spark-1 spark-1.novalocal
10.38.27.237 spark-2 spark-2.novalocal
10.38.29.207 spark-3 spark-3.novalocal
10.38.29.243 spark-4 spark-4.novalocal
```

NOTE: You can run the commands in parallel in all instances using `clustershell` with a command like:
```
clush -l cesgaxuser -bw spark-[1-4] uptime
```

For example to add the address to the hosts file you can create a hosts.spark file locally and then:
```
clush -l cesgaxuser -bw spark-[1-4] --copy hosts.spark --dest /tmp
clush -l cesgaxuser -bw spark-[1-4] 'cat /etc/hosts /tmp/hosts.spark > hosts.all'
clush -l cesgaxuser -bw spark-[1-4] sudo cp -f hosts.all /etc/hosts
```


Install updates:
```
sudo dnf -y update
```

Reboot the instances:
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

Download & Install Spark:
```
curl -L -O https://dlcdn.apache.org/spark/spark-3.3.0/spark-3.3.0-bin-hadoop3.tgz
tar xzvf spark-3.3.0-bin-hadoop3.tgz
```

On the master node execute:
```
spark-3.3.0-bin-hadoop3/sbin/start-master.sh
```

Look at the log to verify everything run correctly and check the spark master url:
```
tail spark-3.3.0-bin-hadoop3/logs/spark-cesgaxuser-org.apache.spark.deploy.master.Master-1-spark-1.novalocal.out
```

You should see something like:
```
Utils: Successfully started service 'sparkMaster' on port 7077.
Master: Starting Spark master at spark://spark-1.novalocal:7077
Utils: Successfully started service 'MasterUI' on port 8080.
Master: I have been elected leader! New state: ALIVE
```
as you can see, in this case, the master url is: spark://spark-1.novalocal:7077

Now we can start each of the workers (one in each additional node: spark-[2-4]):
```
spark-3.3.0-bin-hadoop3/sbin/start-worker.sh spark://spark-1.novalocal:7077
```

Look at the log to verify everything run fine:
```
tail spark-3.3.0-bin-hadoop3/logs/spark-cesgaxuser-org.apache.spark.deploy.worker.Worker-1-spark-2.novalocal.out
```

Connect to the Master UI at:
```
http://spark-1:8080
```
you should see all workers there.

## Pyspark
To run pyspark first we need to install python in all nodes:
```
sudo dnf install -y python39
```
NOTE: Spark 3.3.0 supports Python 3.7 and above.

Then to start a pyspark session just run:
```
spark-3.3.0-bin-hadoop3/bin/pyspark --master spark://spark-1.novalocal:7077

>>> rdd = sc.parallelize(range(120), 6)
>>> rdd.pipe('/bin/hostname').collect()
```

## spark-defaults.conf
We can also tune the configuration:
```
cp spark-3.3.0-bin-hadoop3/conf/spark-defaults.conf.template spark-3.3.0-bin-hadoop3/conf/spark-defaults.conf
```
Edit spark-defaults.conf and set:
```
spark.master spark://spark-1.novalocal:7077
```

Now you can start pyspark omitting the master url:
```
spark-3.3.0-bin-hadoop3/bin/pyspark
```

## Reference
- https://spark.apache.org/docs/latest/spark-standalone.html
