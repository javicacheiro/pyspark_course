# Kibana/OpenSearch Dashboards

You can connect to your Kibana/OpensSearch Dashboards instance:

    http://opensearch-curso825:5601

![Kibana login](http://bigdata.cesga.es/img/kibana_login.png)

The first time you connect you will be asked to select your tenant: just choose "Private":

![Kibana First Message](http://bigdata.cesga.es/img/kibana_first_message.png)

Now you will land in the "Home" screen:

![Kibana First Message](http://bigdata.cesga.es/img/kibana_home.png)

## Discover view
In other to explore data first you have to define a `index pattern`.

You create it under `Management > Stack Management: Index patterns`.

![Kibana Menu](http://bigdata.cesga.es/img/kibana_menu.png)

There you press the button "Create index pattern" and you give the `index patter name`, for example `movies*` then you press next and, if you have a `primary time field` in your documents you can indicate it in the second step.

![Kibana create index 1](http://bigdata.cesga.es/img/kibana_create_index_1.png)

![Kibana create index 2](http://bigdata.cesga.es/img/kibana_create_index_2.png)

After doing this you will be able to select `movies*` in the Discover view and start exploring the data.

In the right panel you can select which of the available fields to include or exclude (`_source`).

In the search box you can type queries using the `Dashboards Query Language` or the `Lucene` syntax we have already seen (more on that in the next section).

![Kibana Discover Query](http://bigdata.cesga.es/img/kibana_discover_query.png)

## Dashboards Query Language
Similar to the Query DSL that lets you use the HTTP request body to search for data, you can use the Dashboards Query Language (DQL) in OpenSearch Dashboards to search for data and visualizations.

For example to see all movies that contain the word "harry" in the "title" field you will use:
```
title:harry
```

You can combine queries using the boolean operators `and`, `or` and `not`:
```
title:harry and not title:sally
```

You can use parentheses to group conditions:
```
(title:harry or title:potter) and not title:sally
(title:harry and title:potter) and not title:prince
```

We can also use date and range queries:
```
year > 2010 and year < 2015
```

In the right of the box where you see `DQL` you can turn off `OpenSearch Dashboards Query Language` and then you will be able to use the elasticsearch json syntax we have seen previously (it will show as `Lucene` instead of `DQL`). Just remember that you just have to type the part inside the `query` field. For example:
```
{"match_phrase":{"title":"harry potter"}}
```

Reference to the Dashboards Query Language:
- [Dashboards Query Language](https://opensearch.org/docs/1.3/dashboards/dql)

## Managing indices from Kibana
You can manage indices from kibana: `OpenSearch Plugins > Index Management: Indices`

![Indices](http://bigdata.cesga.es/img/kibana_indices.png)

## Quering Filebeat logs from Kibana
Under `Management > Stack Management: Index patterns` create a index pattern `filebeat-*` if it is not created.

Select a primary time field for use with the global time filter: `@timestamp`.

## Quering Metricbeat logs from Kibana
Under `Management > Stack Management: Index patterns` create a index pattern `metricbeat-*` if it is not created.

Select a primary time field for use with the global time filter: `@timestamp`.

## Exercices
- Lab: Explore the movies index in Kibana
   - Type some queries using the Dashboards Query Language
   - Try also changing to Lucene query format
- Lab: [Demo: Exploring OpenStack logs (why did this instance failed?)](exercises/kibana_exploring_openstack_logs.md)
- Lab: [Demo: Ingest apache logs from bigdata web and explore them using filebeat pre-defined dashboard](exercises/kibana_apache_logs.md)
