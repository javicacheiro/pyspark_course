#!/bin/bash

source ~/bash/opensearch

docker run -it --rm --name logstash --net host opensearchproject/logstash-oss-with-opensearch-output-plugin:7.16.2 -e 'input { stdin { } } output {
   opensearch {
     hosts => ["https://'${OPENSEARCH_HOST}':'${OPENSEARCH_PORT}'"]
     index => "logstash-stdin-%{+YYYY.MM.dd}"
     user => "'${OPENSEARCH_USER}'"
     password => "'${OPENSEARCH_PASSWD}'"
     ssl => true
     ssl_certificate_verification => false
   }
}'
