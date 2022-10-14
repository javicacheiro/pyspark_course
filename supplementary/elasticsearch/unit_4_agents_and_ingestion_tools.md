# Agents and ingestion tools
## Logstash
This has been a very popular agent, so important that it represents the "L" in the "ELK" stack (Elasticsearch + Logstash + Kibana).

Nowdays it is being replaced by more lightweight clients like `filebeat` and logstash can be used as a intermediate service between `filebeat` and `elasticsearch`.

### Stdin input plugin
The most basic plugin is the `stdin` input plugin that reads from stdin and converts each line in a document.

Lab: [Creating documents from stdin](logstash/input_stdin.sh)
- Upload the scripts with the configuration:
    ```
    scp -r bash cesgaxuser@opensearch-curso825:
    ```
- Connect to the OpenSearch instance and copy the config to the
    ```
    sudo rsync -av bash /root
    ```
- Upload the script to your OpenSearch instance
    ```
    scp logstash_input_stdin.sh cesgaxuser@opensearch-curso825:
    ```
- Connect to your OpenSearch instance and run.
    ```
    sudo ./logstash_input_stdin.sh
    ```
- Review the script, as you can see documents will be added to an index named: `logstash-stdin-%{+YYYY.MM.dd}`
- Run the script and write some lines of text and then see how they appear in elasticsearch.
- Look at the inserted documents:
    ```
    curl --insecure --user admin:admin -X GET "https://opensearch-curso825:9200/opensearch-logstash-test-$(date +%Y.%m.%d)/_search?pretty=true"
    ```

You will see:
```
{
  "took" : 3,
  "timed_out" : false,
  "_shards" : {
    "total" : 1,
    "successful" : 1,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : {
      "value" : 2,
      "relation" : "eq"
    },
    "max_score" : 1.0,
    "hits" : [
      {
        "_index" : "logstash-stdin-2022.10.14",
        "_type" : "_doc",
        "_id" : "mpyP1YMBWZr1S4syU_fO",
        "_score" : 1.0,
        "_source" : {
          "@timestamp" : "2022-10-14T08:14:43.027Z",
          "host" : "opensearch-curso825.novalocal",
          "message" : "Line 1",
          "@version" : "1"
        }
      },
      {
        "_index" : "logstash-stdin-2022.10.14",
        "_type" : "_doc",
        "_id" : "nJyP1YMBWZr1S4syWvfm",
        "_score" : 1.0,
        "_source" : {
          "@timestamp" : "2022-10-14T08:14:45.366Z",
          "host" : "opensearch-curso825.novalocal",
          "message" : "Line 2",
          "@version" : "1"
        }
      }
    ]
  }
}
```

Reference:
- [Stdin input plugin](https://www.elastic.co/guide/en/logstash/7.10/plugins-inputs-stdin.html)

### RSS input plugin
Lab: [Consuming a RSS feed](logstash/input_rss.sh)

- Upload the scripts with the configuration:
    ```
    scp -r bash cesgaxuser@opensearch-curso825:
    ```
- Connect to the OpenSearch instance and copy the config to the
    ```
    sudo rsync -av bash /root
    ```
- Upload the logstash script to your OpenSearch instance
    ```
    scp logstash_input_rss.sh cesgaxuser@opensearch-curso825:
    ```
- Connect to your OpenSearch instance and run.
    ```
    sudo ./logstash_input_rss.sh
    ```
- Review the script, as you can see documents will be added to an index named: `logstash-rss-%{+YYYY.MM.dd}`
- Run the script and write some lines of text and then see how they appear in elasticsearch.
- Look at the inserted documents:
    ```
    curl --insecure --user admin:admin -X GET "https://opensearch-curso825:9200/logstash-rss-$(date +%Y.%m.%d)/_search?pretty=true"
    # Or just one document
    curl --insecure --user admin:admin -X GET -H "Content-Type: application/json" "https://opensearch-curso825:9200/logstash-rss-$(date +%Y.%m.%d)/_search?pretty=true" -d '{"size": 1}'
    ```

You will see:
```
{
  "took" : 2,
  "timed_out" : false,
  "_shards" : {
    "total" : 1,
    "successful" : 1,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : {
      "value" : 55,
      "relation" : "eq"
    },
    "max_score" : 1.0,
    "hits" : [
      {
        "_index" : "logstash-rss-2022.10.14",
        "_type" : "_doc",
        "_id" : "SZ2p1YMBWZr1S4syjQud",
        "_score" : 1.0,
        "_source" : {
          "Feed" : "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
          "@version" : "1",
          "message" : "Prompted by the expanded strikes, European countries made plans to develop joint air defenses and to train Ukrainian soldiers on European Union soil.",
          "title" : "Death Toll Rises as Russia Bombards Ukraine’s Cities for a Fourth Day",
          "link" : "https://www.nytimes.com/2022/10/13/world/europe/russia-ukraine-missiles-deaths.html",
          "@timestamp" : "2022-10-14T08:43:21.470Z",
          "published" : "2022-10-14T07:23:10.000Z",
          "author" : null,
          "tags" : [
            "rss",
            "news"
          ]
        }
      }
    ]
  }
}
```


NOTE: In this case we are using a plugin that is not included by default so the script takes care of installing it with:
```
logstash-plugin install logstash-input-rss
```

You can see all available plugins running:
```
sudo docker run -it --rm opensearchproject/logstash-oss-with-opensearch-output-plugin:7.16.2 /bin/bash -c "logstash-plugin list"
```

Reference:
- [RSS input plugin](https://www.elastic.co/guide/en/logstash/7.10/plugins-inputs-rss.html)

### Twitter input plugin
Lab: [Consuming tweets](logstash/input_twitter.sh)

NOTE: Unfortunately the `twitter` input plugin 7.x does not work with the new Twitter API v2 and the old one is not accessible any more for new accounts.
Even the latest version of the `twitter` input plugin v4.1.0 does not support Twitter API v2.

Reference:
- [Twitter input plugin](https://www.elastic.co/guide/en/logstash/7.10/plugins-inputs-twitter.html)

## Filebeat
- Lab: [Filebeat installation](exercises/filebeat.md) 

## Metricbeat
- Lab: [Metricbeat installation](exercises/metricbeat.md) 

## References
- [Agents and ingestion tools](https://opensearch.org/docs/latest/clients/agents-and-ingestion-tools/index/)
