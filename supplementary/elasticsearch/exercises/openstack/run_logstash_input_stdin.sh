#!/bin/bash

docker run -it --rm --name logstash --net host opensearchproject/logstash-oss-with-opensearch-output-plugin:7.16.2 -e 'input { stdin { } } output {
   opensearch {
     hosts => ["https://localhost:9200"]
     index => "opensearch-logstash-test-%{+YYYY.MM.dd}"
     user => "admin"
     password => "admin"
     ssl => true
     ssl_certificate_verification => false
   }
}'
