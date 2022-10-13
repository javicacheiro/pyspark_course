# Exploring OpenStack logs with Kibana

In this case we will be using one of the OpenSearch production clusters at CESGA.

This cluster receives all the logs from all the servers of the OpenStack CESGA production cluster.

The OpenStack CESGA cluster is deployed in HA mode and all services are replicated for fault-tolerance but this makes tracking logs much more difficult. OpenStack itself is quite difficult to track if you try to go to each service log because OpenStack involves a lot of individual services each one with a particular responsability.

Going server through server looking at the logs would be impractical, for this reason we have `filebeat` configured in each of the servers to send the logs to OpenSearch.


In this example we will be looking at the reason behind the following error returned in Horizon (the OpenStack web interface) when we tried to run a VM:
```
Error: Failed to perform requested operation on instance "test-24", the instance has an error status: Please try again later [Error: Build of instance d892d127-6381-4f17-a019-7581c3bf10ad aborted: Failed to allocate the network(s), not rescheduling.].
```

We connect to Kibana:

    http://kibana-prod:5601

## Index pattern
In the menu we go to `Management > Stack Management: Index Patterns`.

There we can see that we have the `filebeat-*` index pattern already configured which is also the default index pattern.

If we click on it we can see all fiels in the `filebeat-*` index: 1158 fields!!

## Indexes
Now we go to the menu `OpenSearch Plugins > Index Management: Indices`.

There we can see a list of all the indices.

We can filter by the word `filebeat` in the search box, and we will see that there is a filebeat index for each day:
- filebeat-7.12.1-2022.10.01
- filebeat-7.12.1-2022.10.02
- ...

This is a common practice to avoid index growing very large.

## Discover
Now we will go to the menu `OpenSearch Dashboards > Discover`


In the left panel, under `Available fields` we can add more fields to display in the results.

[Filebeat System] Syslog dashboard ECS



We will be looking in the logs for the instance with uuid: `d892d127-6381-4f17-a019-7581c3bf10ad`.

The field we are interested in is the field `message` so we will type the following in the search box:
```
message:"d892d127-6381-4f17-a019-7581c3bf10ad"
```

Expand the time range if needed.

Select the fields:
- host.name
- message

We can see that there are messages related to this instance expanding from 16:35 to 16:44 on Oct 13.

![Demo vm failure 1](kibana_demo_openstack_vm_failure_1.png)

Scrolling we can see that there are different host involved in the creation of the VM and we can see the timeline of events.

We can restrict the results keeping only the error lines:
```
message:"d892d127-6381-4f17-a019-7581c3bf10ad" and message:error
```

![Demo vm failure 2](kibana_demo_openstack_vm_failure_2.png)

And we can see that the follong message in c27-20:
```
2022-10-13 16:41:12.089 7 ERROR nova.compute.manager [req-45229fd8-d576-477d-acf3-86802f652102 b48087604804c6800108258c2c0f2e0f3c977d63adf12cf4c735eabeb065e041 6c6eee826eaa4391a52b2b4170189c13 - 36f8699af54f43faa1ae244b2488ad6d default] [instance: d892d127-6381-4f17-a019-7581c3bf10ad] Instance failed to spawn: nova.exception.VirtualInterfaceCreateException: Virtual Interface creation failed
```

Taking the request idenfier `req-45229fd8-d576-477d-acf3-86802f652102 b48087604804c6800108258c2c0f2e0f3c977d63adf12cf4c735eabeb065e041` we can track back the error:
```
message:"req-45229fd8-d576-477d-acf3-86802f652102 b48087604804c6800108258c2c0f2e0f3c977d63adf12cf4c735eabeb065e041"
```

And we can see:
```
2022-10-13 16:41:11.503 7 WARNING nova.virt.libvirt.driver [req-45229fd8-d576-477d-acf3-86802f652102 b48087604804c6800108258c2c0f2e0f3c977d63adf12cf4c735eabeb065e041 6c6eee826eaa4391a52b2b4170189c13 - 36f8699af54f43faa1ae244b2488ad6d default] [instance: d892d127-6381-4f17-a019-7581c3bf10ad] Timeout waiting for [('network-vif-plugged', '0f0de1cd-2172-4885-b017-446186ab3b06')] for instance with vm_state building and task_state spawning: eventlet.timeout.Timeout: 300 seconds
```

Let's track only error messages:
```
message:"req-45229fd8-d576-477d-acf3-86802f652102 b48087604804c6800108258c2c0f2e0f3c977d63adf12cf4c735eabeb065e041" and message:error
```

We wee a message from c27-33 at 16:35:45.637 which seems as the final reason of the issue: connection lostwith the mysql database (galera in this case):
```
2022-10-13 16:35:44.344 52 ERROR sqlalchemy.pool.impl.QueuePool [req-45229fd8-d576-477d-acf3-86802f652102 b48087604804c6800108258c2c0f2e0f3c977d63adf12cf4c735eabeb065e041 6c6eee826eaa4391a52b2b4170189c13 - 36f8699af54f43faa1ae244b2488ad6d default] Exception during reset or similar: pymysql.err.OperationalError: (2013, 'Lost connection to MySQL server during query')
```

We could now go and review the galera logs, but we have already seen how to track the root cause of an issue to a given service with the help of ElasticSearch.

## Creating visualizations
We can now create some basic visualizations in the Visualizations panel.

### VM instantiation
Type: Vertical Bar
Source: filebeat-*
Metrics: Y-axis Count
Buckets:
- X-axis: Date Histogram: @timestamp
- Split series: terms: host.hostname

Search:
```
message:"d892d127-6381-4f17-a019-7581c3bf10ad"
```

Finally press the "Update" button and we can save it for later use as "OpenStack - VM failure".

![Demo vm failure 3](http://bigdata.cesga.es/img/kibana_demo_openstack_vm_failure_3.png)

### OpenStack - Errors
Type: Vertical Bar
Source: filebeat-*
Metrics: Y-axis Count
Buckets:
- X-axis: Date Histogram: @timestamp
- Split series: terms: host.hostname

![Visualization: OpenStack Errors](http://bigdata.cesga.es/img/kibana_demo_visualization_openstack_errors.png)

### OpenStack - Logs generated per server
Type: Pie
Source: filebeat-*
Metrics: Slice size: Count
Buckets:
- Split slices: host.hostname
Options: Show labels

![Visualization: OpenStack Logs per Server](http://bigdata.cesga.es/img/kibana_demo_visualization_openstack_logs_per_server.png)
