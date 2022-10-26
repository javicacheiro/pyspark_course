## Installing Opensearch/Kibana/Logstash
## Starting the VM on Openstack
Instantiate 3 VM in Openstack:
- Create a keypair importing a existing ssh key:  Compute -> Key Pairs: Import Public Key
- Compute -> Instances: Launch Instance:
  - Instance Name: opensearch-curso825
  - Count: 3
  - Source: baseos-Rocky-8.5-v2
  - Flavor: 
    - m1.medium: 4GB, 2 cores (this is more than enough for the lab, but you have to edit the `openstack/run_docker-opensearch_version.sh` helper script and reduce the memory)
    - m1.xlarge: 16GB RAM, 8 cores (for production)
  - Networks: provnet-formacion-vlan-133
  - Security Groups: default
    NOTE: The default security group is already configured to enable communication between the instances
  - Key Pair: your imported key pair

## Configuring an OpenSearch Cluster
I will be using [ClusterShell](https://clustershell.readthedocs.io/en/latest/) but you can also run the commands individually in each of the servers.


If you want to use ClusterShell my recommendation is to install it locally in your computer. But as an alternative you can install it in one of the nodes:
```
sudo dnf install epel-release
sudo dnf install clustershell
```
NOTE: You will have to setup remote ssh access with public key.

Add the vm instances to your `/etc/hosts` and to the `/etc/hosts` of the remote servers:
```
# opensearch deployment on openstack
1.2.3.4 opensearch-1 opensearch-1.novalocal
1.2.3.4 opensearch-2 opensearch-2.novalocal
1.2.3.4 opensearch-3 opensearch-3.novalocal
1.2.3.4 kibana kibana.novalocal
```

Now we can proceed:
```
clush -l cesgaxuser -bw opensearch-[1-3] sudo dnf -y update

clush -l cesgaxuser -bw opensearch-[1-3] --copy openstack/docker.repo --dest /tmp
clush -l cesgaxuser -bw opensearch-[1-3] sudo cp /tmp/docker.repo /etc/yum.repos.d
clush -l cesgaxuser -bw opensearch-[1-3] sudo dnf install -y --enablerepo docker docker-ce
clush -l cesgaxuser -bw opensearch-[1-3] sudo systemctl enable docker

# Before running the following commands: Create and attach a data volume to each instance
clush -l cesgaxuser -bw opensearch-[1-3] --copy openstack/configure_data_volume.sh --dest /tmp
clush -l cesgaxuser -bw opensearch-[1-3] sudo /tmp/configure_data_volume.sh

clush -l cesgaxuser -bw opensearch-[1-3] sudo reboot
```

Edit `run_docker-opensearch_version.sh` and set the right IP addresses for the nodes. Then upload it to the VMs and execute it by running:
```
clush -l cesgaxuser -bw opensearch-[1-3] --copy openstack/run_docker-opensearch_version.sh --dest /home/cesgaxuser
clush -l cesgaxuser -bw opensearch-[1-3] sudo /home/cesgaxuser/run_docker-opensearch_version.sh
clush -l cesgaxuser -bw opensearch-[1-3] sudo docker ps

```

NOTE: The `vm.max_map_count` kernel setting must be set to at least 262144 for production use, this is done automatically in the `run_docker-opensearch_version.sh` script.
If you restart the virtual machine then you will have to set it again manually or the opensearch container will not boot:
```
sysctl -w vm.max_map_count=262144
```
You can make this change permanent by adding this line to `/etc/sysctl.conf`.


Verify the installation with:

```
curl --insecure -u admin:admin -XGET 'https://opensearch-1:9200/_cat/health?v&pretty'
http --verify no --auth admin:admin 'https://opensearch-1:9200/_cat/health?v&pretty'
```

## Kibana
Once elasticsearch has started you can run kibana.

You will have to edit the `run_kibana-opensearch_version.sh` to point to the right opensearch instance addresses:
```
clush -l cesgaxuser -bw kibana --copy openstack/run_kibana-opensearch_version.sh --dest /home/cesgaxuser
clush -l cesgaxuser -bw kibana sudo /home/cesgaxuser/run_kibana-opensearch_version.sh
```

Go to kibana:

    http://kibana:5601

NOTE: Be careful because kibana by default would resolve to kibana.service.int.cesga.es (the production one)

credentials are: admin/admin

To destroy the running cluster:
```
clush -l cesgaxuser -bw opensearch-[1-3] 'sudo docker rm -f $(hostname -s)'
clush -l cesgaxuser -bw opensearch-[1-3] sudo rm -rf /data/opensearch

clush -l cesgaxuser -bw kibana sudo docker rm -f kibana
```

## Logstash
In this case, instead of using a dedicated node we will be using the kibana node to run logstash.

Copy the helper script:
```
scp ../logstash/input_stdin.sh  cesgaxuser@kibana:run_logstash_input_stdin.sh
```

You will have to set the OPENSEARCH_HOST and OPENSEARCH_PORT variables.
```
export OPENSEARCH_HOST="1.2.3.4"
export OPENSEARCH_PORT="9200"
```

Running logstash:
```
sudo ./run_logstash_input_stdin.sh
```

Later on in the course we will see sample configurations for running logstash.

Right now with the provided script we will run logstash so that it reads stdin and publishes to the opensearch index: `opensearch-logstash-test-%{+YYYY.MM.dd}`.

The `stdin` input plugin will read events from standard input, each event is assumed to be one line.

Write some lines of text and then see how they appear in elasticsearch.

See the output of logstash:
```
curl --insecure --user admin:admin -X GET "https://opensearch-curso825:9200/opensearch-logstash-test-$(date +%Y.%m.%d)/_search?pretty=true"
```

If you just want one document:
```
curl --insecure --user admin:admin -X GET -H "Content-Type: application/json" "https://opensearch-curso825:9200/opensearch-logstash-test-$(date +%Y.%m.%d)/_search?pretty=true" -d '{"size": 1}'
```

As an alternative to curl you can use httpie (no need for the pretty option):
- [HTTPie](https://httpie.io/)

Installing httpie:
```
sudo dnf install epel-release
sudo dnf install httpie
```

Using httpie:
```
http --verify no --auth admin:admin "https://opensearch-curso825:9200/opensearch-logstash-test-$(date +%Y.%m.%d)/_search"
```

and instead of `-H "Content-Type: application/json"` we can use the `--json` option to indicate that we will be sending a json object in the request body:
```
http --json --verify no --auth admin:admin "https://opensearch-curso825:9200/opensearch-logstash-test-$(date +%Y.%m.%d)/_search" size=1
```

As you can see it is much, much more user friendly than curl.

Finally, we can do some cleaning and remove the index:
```
curl --insecure --user admin:admin -X DELETE https://opensearch-curso825:9200/opensearch-logstash-test-$(date +%Y.%m.%d)
```
