"""Twitter consumer: stores data in OpenSearch

Reads configuration from the following environmental variables:
    - TWITTER_BEARER_TOKEN: Twitter bearer token
    - OPENSEARCH_HOST: ElasticSearch/OpenSearch host
    - OPENSEARCH_PORT: by default it will use port 9200
    - OPENSEARCH_USER: ElasticSearch/OpenSearch user
    - OPENSEARCH_PASSWD: ElasticSearch/OpenSearch password

You can store the configuration variables in a file and then load them:

    source ~/bash/twitter
    source ~/bash/opensearch

"""
import tweepy
from opensearchpy import OpenSearch
import os

bearer_token = os.environ['TWITTER_BEARER_TOKEN']

host = os.environ['OPENSEARCH_HOST']
port = os.environ['OPENSEARCH_PORT']
auth = (os.environ['OPENSEARCH_USER'], os.environ['OPENSEARCH_PASSWD'])

# OpenSearch index configuration
index_name = 'twitter-supercomputing'

index_body = {
  'settings': {
    'index': {
      'number_of_shards': 1,
      'number_of_replicas': 0
    }
  }
}

# In production modify the following code to verify certs
es = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_compress=True,
    http_auth=auth,
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False
)

class TweetPrinter(tweepy.StreamingClient):

    def on_connect(self):
        print("Connected")

    def on_tweet(self, tweet):
        print('---')
        # We can print the whole tweet
        #print(tweet)
        # Or just some fields
        print(tweet.created_at)
        print(tweet.text)
        #print(tweet.author_id)
        #print(tweet.geo)
        #print(tweet.conversation_id)
        # The data is inside the data field
        #print(tweet.data)
        es.index(
            index = index_name,
            body = tweet.data
        )


def delete_previous_rules():
    client = tweepy.StreamingClient(bearer_token)
    result = client.get_rules()
    rule_ids = []
    for rule in result.data:
        print(f"rule marked to delete: {rule.id} - {rule.value}")
        rule_ids.append(rule.id)
    if len(rule_ids) > 0:
        client.delete_rules(rule_ids)

if __name__ == '__main__':

    # Create the index only the first time
    if not es.indices.exists(index_name):
        response = es.indices.create(index_name, body=index_body)
        print('\nCreating ElasticSearch index:')
        print(response)

    printer = TweetPrinter(
        bearer_token,
        wait_on_rate_limit=True)
    # Option 1: Get a sample of the data
    #printer.sample()
    # Option 2: Filter given tweets
    delete_previous_rules()
    printer.add_rules(tweepy.StreamRule("supercomputer lang:en"))
    printer.add_rules(tweepy.StreamRule("supercomputing lang:en"))
    printer.filter(tweet_fields=['author_id', 'conversation_id', 'created_at', 'geo', 'lang'])
