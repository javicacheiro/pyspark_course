## Installing Opensearch/Kibana/Logstash
## Starting the VM on Openstack
Instantiate 3 VM in Openstack:
- Create a keypair importing a existing ssh key:  Compute -> Key Pairs: Import Public Key
- Compute -> Instances: Launch Instance:
  - Instance Name: opensearch-curso825
  - Count: 3
  - Source: baseos-Rocky-8.5-v2
  - Flavor: m1.medium
  - Networks: provnet-formacion-vlan-133
  - Security Groups: default
    NOTE: The default security group is already configured to enable communication between the instances
  - Key Pair: your imported key pair

## Configuring an OpenSearch Cluster
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
Once elasticsearch has started you can run kibana:
```
clush -l cesgaxuser -bw kibana --copy openstack/run_kibana-opensearch_version.sh --dest /home/cesgaxuser
clush -l cesgaxuser -bw kibana sudo /home/cesgaxuser/run_kibana-opensearch_version.sh
```

Go to kibana:

    http://10.38.29.17:5601

NOTE: Be careful because kibana by default would resolve to kibana.service.int.cesga.es (the production one)

credentials are: admin/admin

To destroy the running cluster:
```
clush -l cesgaxuser -bw opensearch-[1-3] 'sudo docker rm -f $(hostname -s)'
clush -l cesgaxuser -bw opensearch-[1-3] sudo rm -rf /data/opensearch

clush -l cesgaxuser -bw kibana sudo docker rm -f kibana
```

## Logstash
Running logstash:
```
clush -l cesgaxuser -bw opensearch-[1-3] --copy openstack/run_logstash.sh --dest /home/cesgaxuser
sudo ./run_logstash.sh
```

See the output of logstash:
```
# using curl
curl --insecure --user admin:admin 'https://opensearch-1:9200/opensearch-logstash-docker-2022.08.13/_search?pretty=true'
curl --insecure --user admin:admin 'https://opensearch-1:9200/opensearch-logstash-docker-2022.08.13/_search?pretty=true' -d '{"size": 1}'

# using httpie (no need for the pretty option)
http --verify no --auth admin:admin 'https://opensearch-1:9200/opensearch-logstash-docker-2022.08.13/_search'
http --json --verify no --auth admin:admin 'https://opensearch-1:9200/opensearch-logstash-docker-2022.08.13/_search' size=1
```

Cleaning:
```
curl --insecure --user admin:admin -X DELETE https://opensearch-1:9200/opensearch-logstash-docker-2022.08.13
```
