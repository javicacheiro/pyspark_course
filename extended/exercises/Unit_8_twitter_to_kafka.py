"""Twitter consumer: stores data in Kafka

Reads configuration from the following environmental variables:
    - TWITTER_BEARER_TOKEN: Twitter bearer token
    - KAFKA_BROKER: Kafka Broker, it can include port eg. "10.38.28.103:9092"

You can store the configuration variables in a file and then load them:

    source ~/bash/twitter

Rember to create the Kafka topic first using something similar to:

    kafka-topics.sh --bootstrap-server $BROKER --topic twitter --create --partitions 3 --replication-factor 1

"""
import tweepy
from kafka import KafkaProducer
import json
import os

bearer_token = os.environ['TWITTER_BEARER_TOKEN']
broker = os.environ['KAFKA_BROKER']

producer = KafkaProducer(bootstrap_servers='10.38.28.103:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))


class TwitterExporter(tweepy.StreamingClient):
    """Consumes tweets and exports them to kafka"""
    def on_connect(self):
        print("Connected")

    def on_tweet(self, tweet):
        print('---')
        print(tweet)
        # tweet.data contains the tweet data
        producer.send("twitter", tweet.data)


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
    exporter = TwitterExporter(
        bearer_token,
        wait_on_rate_limit=True)
    # Option 1: Get a sample of the data
    #exporter.sample()
    # Option 2: Filter given tweets
    delete_previous_rules()
    exporter.add_rules(tweepy.StreamRule("putin lang:en"))
    #exporter.add_rules(tweepy.StreamRule("rusia lang:es"))
    #exporter.add_rules(tweepy.StreamRule("russia lang:en"))
    #exporter.add_rules(tweepy.StreamRule("cesga"))
    exporter.filter(tweet_fields=['author_id', 'conversation_id', 'created_at', 'geo', 'lang'])
