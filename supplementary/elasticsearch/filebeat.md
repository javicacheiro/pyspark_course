# Filebeat installation
Download filebeat:
```
# OSS version
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-oss-7.12.1-x86_64.rpm
```

Install it:
```
sudo rpm -ivh filebeat-oss-7.12.1-x86_64.rpm
```

We can now configure the `paths` where filebeat will look for logs as well as define tags for our cluster:
```
sudo vi /etc/filebeat/filebeat.yml
```
For example we can set:
```
- type: log

  enabled: true

  paths:
    - /var/log/*.log
    - /var/log/messages
    - /var/log/cron
    - /var/log/*/*.log

tags: ["bigdata-lab", "opensearch-curso825"]

logging.level: warning
```

Also set up your OpenSearch instance as the output:
```
output.elasticsearch:
  hosts: ["localhost:9200"]
  protocol: "https"
  ssl.verification_mode: "none"
  username: "admin"
  password: "admin"
```

There are different data collection modules for popular tools:
- To see the available data collection modules:
    ```
    sudo filebeat modules list
    ```
- For example if we had mysql installed we could enable the mysql module:
    ```
    sudo filebeat modules enable system mysql
    ```
- We can also edit the modules config and customize them, they are just configuration files under `/etc/filebeat/modules.d/`:
    ```
    ls /etc/filebeat/modules.d/
    ```

## A note on OpenSearch
Since we are using OpenSearch instead of ElasticSearch we must enable compatibility mode so filebeat setup is able to work correctly uploading the assets (index, dashboard, etc):
```
curl --insecure -u admin:admin -XPUT --header 'Content-Type: application/json' 'https://localhost:9200/_cluster/settings' -d '
{
  "persistent" : {
    "compatibility.override_main_response_version" : true
  }
}'
```

If the command was succesful we will get the following output:
```
{"acknowledged":true,"persistent":{"compatibility":{"override_main_response_version":"true"}},"transient":{}}
```

## Set up the assets
In case we are using ElasticSearch we could just run:
```
filebeat setup -e
```

But, for the moment, when using OpenSearch we will have to do the steps manually.

### Step 1: Manually load the index template in OpenSearch
Export the filebeat index template:
```
sudo filebeat export template > filebeat.template.json
```

We now have to edit it and remove the lifecycle clause (see below):
```
vi filebeat.template.json
```
Remove the following part:
```
"lifecycle": {
        "name": "filebeat",
        "rollover_alias": "filebeat-7.12.1"
      },
```
Now we will load the template in OpenSearch:
```
curl --insecure -u admin:admin -XPUT --header 'Content-Type: application/json' https://localhost:9200/_template/filebeat-7.12.1 -d@filebeat.template.json
```

If the command was succesful we will get the following output:
```
{"acknowledged":true}
```

### Step 2: Manually load the index-pattern in Kibana
Export the index-pattern:
```
sudo filebeat export index-pattern --es.version 7.12.1 > filebeat.index-pattern.json
```
Manually load it in kibana (in our case is running in localhost):
```
curl --insecure -u admin:admin -XPOST --header 'osd-xsrf: true' --header 'Content-Type: application/json' 'http://localhost:5601/api/opensearch-dashboards/dashboards/import?force=true' -d@filebeat.index-pattern.json
```

### Step 3: Load the relevant dashboards in Kibana
Filebeat provides different sample dashboards that we can use in Kibana. They are under:
```
ls /usr/share/filebeat/kibana/7/dashboard/
```

We will load the `syslog` and `ssh-login-attempts` dashboards in our Kibana instance:
```
# Filebeat-syslog.json
curl --insecure -u admin:admin -XPOST --header 'osd-xsrf: true' --header 'Content-Type: application/json' 'http://localhost:5601/api/opensearch-dashboards/dashboards/import?exclude=index-pattern&force=true' -d@/usr/share/filebeat/kibana/7/dashboard/Filebeat-syslog.json

# Filebeat-ssh-login-attempts.json
curl --insecure -u admin:admin -XPOST --header 'osd-xsrf: true' --header 'Content-Type: application/json' 'http://localhost:5601/api/opensearch-dashboards/dashboards/import?exclude=index-pattern&force=true' -d@/usr/share/filebeat/kibana/7/dashboard/Filebeat-ssh-login-attempts.json
```

## Start filebeat
Finally we can now start the filebeat service:
```
sudo systemctl start filebeat
```

We can check that it is running with:
```
sudo systemctl status filebeat
```

## Debugging problems
```
# Test we are able to write to output 
filebeat test output
# Run interactively with debug level
filebeat -e -d '*'
```

Apply tuned profile:
```
root@opensearch-curso825 log]# tuned-adm active
Current active profile: virtual-guest
[root@opensearch-curso825 log]# tuned-adm profile throughput-performance
```

Increase number of open files
```
sysctl -w fs.file-max=6526709
```

## References
- [OpenSearch: Agents and ingestion tools](https://opensearch.org/docs/latest/clients/agents-and-ingestion-tools/index/)
- [How to setup filebeat if using opensearch](https://www.electricbrain.com.au/pages/analytics/opensearch-vs-elasticsearch.php)
