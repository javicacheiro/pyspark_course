# Ingesting data from Twitter
## Updating the configuration files
The configurations files are under the `twitter/bash` directory.

You will need a Twitter developer account so you can obtain a TWITTER_BEARER_TOKEN. Once you have it edit `bash/twitter`.

You will also have to configure the OpenSearch location in `bash/opensearch`.

## Upload files
Upload the files to the opensearch instance.
```
scp -r twitter cesgaxuser@opensearch-curso825:
```

## Installing dependencies
```
sudo dnf install python39

cd twitter
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

This will install the following dependencies:
- opensearch-py: a module to use opensearch
- tweepy: a module to use twitter

## Decide what you want to consume
You can edit the `twitter/twitter_to_opensearch.py` and customize which tweets to consume and in which opensearch index to store them.

## Run the program
```
source bash/twitter
source bash/opensearch
python3 twitter_to_opensearch.py
```

## Look at the inserted documents:
```
curl --insecure --user admin:admin -X GET "https://opensearch-curso825:9200/twitter-supercomputing/_search?pretty=true"
```
