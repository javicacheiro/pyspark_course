#!/bin/bash

source ~/bash/twitter
source ~/bash/opensearch

docker run -it --rm --name logstash --net host opensearchproject/logstash-oss-with-opensearch-output-plugin:7.16.2 -e '
input {
  twitter {
    consumer_key => "'${TWITTER_CONSUMER_KEY}'"
    consumer_secret => "'${TWITTER_CONSUMER_SECRET}'"
    oauth_token => "'${TWITTER_OAUTH_TOKEN}'"
    oauth_token_secret => "'${TWITTER_OAUTH_TOKEN_SECRET}'"
    keywords => ["supercomputing", "hpc"]
    full_tweet => true
    
  }
}

output {
   opensearch {
     hosts => ["https://'${OPENSEARCH_HOST}':'${OPENSEARCH_PORT}'"]
     index => "twitter"
     user => "'${OPENSEARCH_USER}'"
     password => "'${OPENSEARCH_PASSWD}'"
     ssl => true
     ssl_certificate_verification => false
   }

  stdout {
    codec => "rubydebug"
  }
}'
