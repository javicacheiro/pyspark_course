# Visualizing Apache Logs in Kibana
We will see this in action in our OpenSearch production cluster.

The `bigdata.cesga.gal` web server is configured to send logs to OpenSearch and I have already loaded the dashboad from filebeat.
```
/usr/share/filebeat/kibana/7/dashboard/Filebeat-apache.json
```

I have also enabled the filebeat `apache` module:
```
filebeat modules enable apache
systemctl restart filebeat
```

## Discover
First we can see that logs from `bigdata.cesga.gal` are reaching OpenSearch by going to the Discover view in Kibana and searching for:
```
host.name:"bigdata.cesga.gal"
```

![Discover](http://bigdata.cesga.es/img/kibana_bigdata_visualize.png)

## Dashboard
And now we can also see the dashboard that comes with filebeat and that we have previously loaded:

We see it appears in the list:

![Dashboard List](http://bigdata.cesga.es/img/kibana_bigdata_dashboard_list.png)

And if we open it we see it in action:

![Dashboard](http://bigdata.cesga.es/img/kibana_bigdata_dashboard.png)
