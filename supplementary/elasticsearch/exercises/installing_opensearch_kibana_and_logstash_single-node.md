## Installing Opensearch/Kibana/Logstash
## Starting the VM on Openstack
Instantiate 1 VM in Openstack:
- Create a keypair importing a existing ssh key:  Compute -> Key Pairs: Import Public Key
- Compute -> Instances: Launch Instance:
  - Instance Name: opensearch-curso825
  - Source: baseos-Rocky-8.5-v2
  - Flavor: m1.medium
  - Networks: provnet-formacion-vlan-133
  - Security Groups: default
    NOTE: The default security group is already configured to enable communication between the instances
  - Key Pair: your imported key pair

## OpenSearch

NOTE: I will be referencing the VM as `opensearch-curso825`, you can do something similar if you add this alias to your `/etc/hosts` file, but you can also use its IP address instead. Add it also to the VM:
```
10.X.X.X opensearch-curso825 opensearch-curso825.novalocal
```

We will be using docker, so first copy some files into the VM:
```
scp openstack/docker.repo openstack/run_docker-opensearch_version_single-node.sh cesgaxuser@opensearch-curso825:
```

Then, connect using SSH to the VM with the user `cesgaxuser` and then run the following:

```
sudo dnf -y update
sudo cp docker.repo /etc/yum.repos.d
sudo dnf install -y --enablerepo docker docker-ce
sudo systemctl enable docker

sudo mkdir -p /data/opensearch

# Replace 10.X.X.X with the IP of your VM and curso825 with your account number
sudo bash -c 'echo "10.X.X.X opensearch-curso825 opensearch-curso825.novalocal" >> /etc/hosts'

sudo reboot
```

And now we can start opensearch:
```
sudo ./run_docker-opensearch_version_single-node.sh
```

Check that the docker container is running and look at the logs:
```
sudo docker ps
sudo docker logs opensearch-curso825
```
It will take some time, but you should see a message like the following when everything is ready:
```
[opensearch-curso825] Move metadata has finished.
```

Verify the installation with:
```
curl --insecure -u admin:admin -XGET 'https://opensearch-curso825:9200/_cat/health?v&pretty'
```
You should see that the `status` is `green`.

NOTE: The `vm.max_map_count` kernel setting must be set to at least 262144 for production use, this is done automatically in the `run_docker-opensearch_version.sh` script.
If you restart the virtual machine then you will have to set it again manually or the opensearch container will not boot:
```
sysctl -w vm.max_map_count=262144
```
You can make this change permanent by adding this line to `/etc/sysctl.conf`.
```
echo vm.max_map_count=262144 >> /etc/sysctl.conf
```

## Kibana
Once elasticsearch has started you can run kibana.

First we will copy the helper script:
```
scp openstack/run_kibana-opensearch_version_single-node.sh  cesgaxuser@opensearch-curso825:
```

Then we can start kibana:
```
sudo ./run_kibana-opensearch_version_single-node.sh
```

Go to kibana:

    http://opensearch-curso825:5601

credentials are: admin/admin

To destroy the running cluster:
```
sudo docker rm -f $(hostname -s)
sudo rm -rf /data/opensearch

sudo docker rm -f kibana
```

## Logstash
Copy the helper script:
```
scp openstack/run_logstash_input_stdin.sh  cesgaxuser@opensearch-curso825:
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
