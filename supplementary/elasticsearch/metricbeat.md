# Metricbeat installation
Download metricbeat:
```
# OSS version
curl -L -O https://artifacts.elastic.co/downloads/beats/metricbeat/metricbeat-oss-7.12.1-x86_64.rpm
```

Install it:
```
sudo rpm -ivh metricbeat-oss-7.12.1-x86_64.rpm
```

We can now tune the configuration under `/etc/metricbeat/metricbeat.yml`.
```
sudo vim /etc/metricbeat/metricbeat.yml
```

In this case we will increase the logging level and set up your OpenSearch instance as the output:
```
logging.level: warning

output.elasticsearch:
  hosts: ["localhost:9200"]
  protocol: "https"
  ssl.verification_mode: "none"
  username: "admin"
  password: "admin"
```

And now we will enable some metrics collection modules.

We can see the list of available collection modules with:
```
sudo metricbeat modules list
```

We will enable the `linux` and `docker` collection modules:
```
sudo metricbeat modules enable linux docker
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
metricbeat setup -e
```

But, for the moment, when using OpenSearch we will have to do the steps manually.

### Step 1: Manually load the index template in OpenSearch
Export the filebeat index template:
```
sudo metricbeat export template > metricbeat.template.json
```

We now have to edit it and remove the lifecycle clause (see below):
```
vi metricbeat.template.json
```
Remove the following part:
```
"lifecycle": {
        "name": "metricbeat",
        "rollover_alias": "metricbeat-7.12.1"
      },
```
Now we will load the template in OpenSearch:
```
curl --insecure -u admin:admin -XPUT --header 'Content-Type: application/json' https://localhost:9200/_template/metricbeat-7.12.1 -d@metricbeat.template.json
```

If the command was succesful we will get the following output:
```
{"acknowledged":true}
```

### Step 2: Manually load the index-pattern in Kibana
Export the index-pattern:
```
sudo metricbeat export index-pattern --es.version 7.12.1 > metricbeat.index-pattern.json
```
Manually load it in kibana (in our case is running in localhost):
```
curl --insecure -u admin:admin -XPOST --header 'osd-xsrf: true' --header 'Content-Type: application/json' 'http://localhost:5601/api/opensearch-dashboards/dashboards/import?force=true' -d@metricbeat.index-pattern.json
```

### Step 3: Load the relevant dashboards in Kibana
metricbeat provides different sample dashboards that we can use in Kibana. They are under:
```
ls /usr/share/metricbeat/kibana/7/dashboard/
```

We will load the `host-overview` and `docker-overview` dashboards in our Kibana instance:
```
# Metricbeat-host-overview.json
curl --insecure -u admin:admin -XPOST --header 'osd-xsrf: true' --header 'Content-Type: application/json' 'http://localhost:5601/api/opensearch-dashboards/dashboards/import?exclude=index-pattern&force=true' -d@/usr/share/metricbeat/kibana/7/dashboard/Metricbeat-host-overview.json

# Metricbeat-docker-overview.json
curl --insecure -u admin:admin -XPOST --header 'osd-xsrf: true' --header 'Content-Type: application/json' 'http://localhost:5601/api/opensearch-dashboards/dashboards/import?exclude=index-pattern&force=true' -d@/usr/share/metricbeat/kibana/7/dashboard/Metricbeat-docker-overview.json
```

## Start metricbeat
Finally we can now start the metricbeat service:
```
sudo systemctl start metricbeat
```

We can check that it is running with:
```
sudo systemctl status metricbeat
```

## See data arriving to Kibana
We can now go to the `Discover` view in Kibana, we select the `metricbeat-*` index pattern and we should see data coming.

We can also go to the `Dashboards` view and select the dashboards that we have loaded before.

## References
- [OpenSearch: Agents and ingestion tools](https://opensearch.org/docs/latest/clients/agents-and-ingestion-tools/index/)
- [How to setup metricbeat if using opensearch](https://www.electricbrain.com.au/pages/analytics/opensearch-vs-elasticsearch.php)

