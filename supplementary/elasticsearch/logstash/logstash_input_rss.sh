#!/bin/bash

source ~/bash/opensearch

docker run -it --rm --name logstash --net host opensearchproject/logstash-oss-with-opensearch-output-plugin:7.16.2 -e '

input {
  rss {
    url => "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
    interval => 3600
    tags => ["rss", "news"]
  }
}

output {
   stdout {
     codec => rubydebug
   }

   opensearch {
     hosts => ["https://'${OPENSEARCH_HOST}':'${OPENSEARCH_PORT}'"]
     index => "opensearch-logstash-docker-%{+YYYY.MM.dd}"
     user => "'${OPENSEARCH_USER}'"
     password => "'${OPENSEARCH_PASSWD}'"
     ssl => true
     ssl_certificate_verification => false
   }
 }'
