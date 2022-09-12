from __future__ import print_function, division
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from io import BytesIO
import avro.schema
from avro.io import BinaryDecoder, DatumReader
import re
from operator import add, sub
import redis
import requests


INTERVAL = 30
WINDOW = 600
THRESHOLD = 10
REDIS_HOST = '1.2.3.4'
SLACK = 'https://hooks.slack.com/services/T3R0LNMV3/BFN92DJBS/XXXXX'

FLUME_EVENT_SCHEMA = """{
"type": "record",
"name": "Event",
"fields": [
    {"name": "headers", "type": {"type": "map", "values": "string"}},
    {"name": "body", "type": "bytes"}
]}"""


def decode_avro(message):
    schema = avro.schema.parse(FLUME_EVENT_SCHEMA)
    bytes_reader = BytesIO(message)
    decoder = BinaryDecoder(bytes_reader)
    reader = DatumReader(schema)
    return reader.read(decoder)


def dump_record(record):
    print('type: {}, keys: {}, headers: {}'.format(type(record), record.keys(), record['headers']))


def save_rdd(rdd):
    for record in rdd.take(5):
        dump_record(record)


def attacker(body):
    """Return the attacker's IP"""
    attacker_ip = re.compile(r'Failed password for .* from ([\d\.]+) port')
    m = attacker_ip.search(body)
    if m:
        return m.group(1)
    else:
        return 'UNKNOWN'


def accumulate(new, acc):
    if acc is None:
        acc = 0
    return sum(new, acc)


def publish_current(partition, table='current'):
    r = redis.Redis(host=REDIS_HOST)
    for ip, count in partition:
        r.hset(table, ip, count)
        publish_slack('SSH_ATTACK_DETECTOR: {} {} {}'.format(table, ip, count))


def publish_accumulated(partition, table='total'):
    r = redis.Redis(host=REDIS_HOST)
    for ip, count in partition:
        old = r.hget(table, ip)
        if old:
            count += int(old)
        r.hset(table, ip, count)
        publish_slack('SSH_ATTACK_DETECTOR: {} {} {}'.format(table, ip, count))


def publish_slack(msg):
    requests.post(SLACK, json={"text": msg})


if __name__ == '__main__':
    sc = SparkContext(appName='SSH brute-force attack detection')
    ssc = StreamingContext(sc, INTERVAL)
    ssc.checkpoint('checkpoints-ssh')

    kvs = KafkaUtils.createDirectStream(ssc, ['flume.syslog'], {"metadata.broker.list": "1.2.3.4:6667"}, valueDecoder = decode_avro)
    # The flume avro event is in the kafka value (kafka key is empty)
    events = kvs.map(lambda x: x[1])
    # If we are interested just in a given host
    #events.filter(lambda r: r['headers']['host'] == 'adm6702').pprint()

    filtered = events.filter(lambda r: 'Failed password' in r['body'])
    ips = filtered.map(lambda r: (attacker(r['body']), 1))
    counts = ips.reduceByKey(add)
    counts.foreachRDD(lambda rdd: rdd.foreachPartition(publish_accumulated))

    window_counts = ips.reduceByKeyAndWindow(add, sub, WINDOW).filter(lambda (k, v): v >= THRESHOLD)
    window_counts.pprint()
    window_counts.foreachRDD(lambda rdd: rdd.foreachPartition(publish_current))

    #ips_dest = filtered.map(lambda r: (attacker(r['body']), r['headers']['host'])).transform(lambda rdd: rdd.distinct().countByKey())
    #ips_dest.pprint()

    #total_counts = counts.updateStateByKey(accumulate)
    #total_counts.pprint()

    # We write to Redis:
    # status:
    #  {attacker_ip_1: {count: TOTAL_ATTEMPTS, targets: [target1, target2, ...]},
    #   attacker_ip_2: ...}
    #
    # detected: {ip1: count, ip2: count, ...}

    ssc.start()
    ssc.awaitTermination()
    ssc.stop()
